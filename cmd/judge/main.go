// agent-compact judge — local docket viewer for .agent/ directories.
// Single binary, zero dependencies, embeds HTML, auto-opens browser.
//
//	go build -o judge .
//	./judge                    # uses .agent/ in cwd
//	./judge /path/to/.agent    # explicit path
//	./judge -port 9999         # custom port
package main

import (
	_ "embed"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
)

//go:embed judge.html
var indexHTML []byte

type FileEntry struct {
	Path    string `json:"path"`
	Content string `json:"content"`
}

func main() {
	port := flag.Int("port", 0, "port to listen on (0 = auto)")
	noBrowser := flag.Bool("no-browser", false, "don't open browser")
	flag.Parse()

	dir := ".agent"
	if flag.NArg() > 0 {
		dir = flag.Arg(0)
	}

	abs, err := filepath.Abs(dir)
	if err != nil {
		log.Fatalf("bad path: %v", err)
	}

	if info, err := os.Stat(abs); err != nil || !info.IsDir() {
		log.Fatalf("not a directory: %s", abs)
	}

	mux := http.NewServeMux()

	// serve embedded HTML
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			http.NotFound(w, r)
			return
		}
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		w.Write(indexHTML)
	})

	// list all files recursively
	mux.HandleFunc("/api/files", func(w http.ResponseWriter, r *http.Request) {
		var files []FileEntry
		filepath.Walk(abs, func(path string, info os.FileInfo, err error) error {
			if err != nil {
				return nil
			}
			if info.IsDir() {
				if info.Name() == ".git" {
					return filepath.SkipDir
				}
				return nil
			}
			ext := strings.ToLower(filepath.Ext(path))
			if ext != ".md" && ext != ".yaml" && ext != ".yml" && ext != ".py" {
				return nil
			}

			rel, _ := filepath.Rel(abs, path)
			rel = filepath.ToSlash(rel) // normalize to forward slashes

			data, err := os.ReadFile(path)
			if err != nil {
				return nil
			}

			files = append(files, FileEntry{
				Path:    rel,
				Content: string(data),
			})
			return nil
		})

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(files)
	})

	// pick port
	addr := fmt.Sprintf("127.0.0.1:%d", *port)
	ln, err := net.Listen("tcp", addr)
	if err != nil {
		log.Fatalf("listen: %v", err)
	}

	url := fmt.Sprintf("http://%s", ln.Addr().String())
	fmt.Printf("agent-compact docket\n")
	fmt.Printf("  dir:  %s\n", abs)
	fmt.Printf("  url:  %s\n", url)

	if !*noBrowser {
		go openBrowser(url)
	}

	log.Fatal(http.Serve(ln, mux))
}

func openBrowser(url string) {
	var cmd *exec.Cmd
	switch runtime.GOOS {
	case "darwin":
		cmd = exec.Command("open", url)
	case "windows":
		cmd = exec.Command("cmd", "/c", "start", url)
	default:
		cmd = exec.Command("xdg-open", url)
	}
	cmd.Run()
}
