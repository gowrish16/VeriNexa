import React, { useState, useEffect, useRef, memo } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/TextLayer.css";
import "react-pdf/dist/Page/AnnotationLayer.css";
import {
  X,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  Maximize2,
  ExternalLink,
  FileText,
  AlertCircle,
  Sparkles,
  MapPin,
  Loader2,
  RefreshCw
} from "lucide-react";

import "pdfjs-dist/build/pdf.worker.min.mjs";

// Configure pdfjs worker
try {
  pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;
} catch (e) {
  // fallback handled gracefully
}

export default function PdfViewer({ fileUrl, filename, paperId, activeCitation, onClose }) {
  const getTargetPage = (citation) => {
    if (!citation) return 1;
    const target =
      citation.page_num ??
      citation.page_number ??
      citation.page ??
      1;
    const parsed = Number(target);
    return parsed && !isNaN(parsed) && parsed > 0 ? parsed : 1;
  };

  const currentPaperId = paperId || filename || fileUrl || "doc";
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(() => getTargetPage(activeCitation));
  // Default to 1.0 (Fit-to-Width mode)
  const [zoom, setZoom] = useState(1.0);
  const [containerWidth, setContainerWidth] = useState(() => {
    if (typeof window !== "undefined") {
      const w = window.innerWidth;
      return w > 1024 ? Math.floor(w * 0.48) : w - 64;
    }
    return 650;
  });
  const [useIframeFallback, setUseIframeFallback] = useState(false);
  const [isPageRendered, setIsPageRendered] = useState(false);
  const [renderError, setRenderError] = useState(null);
  const [retryKey, setRetryKey] = useState(0);

  const scrollContainerRef = useRef(null);
  const pageContainerRef = useRef(null);
  const retryAttemptRef = useRef(0);

  // Measure container width accurately using ResizeObserver
  useEffect(() => {
    if (!scrollContainerRef.current) return;
    const updateWidth = () => {
      if (scrollContainerRef.current) {
        const measured = scrollContainerRef.current.clientWidth;
        if (measured > 100) {
          setContainerWidth(measured);
        }
      }
    };
    updateWidth();
    const ro = new ResizeObserver(updateWidth);
    ro.observe(scrollContainerRef.current);
    window.addEventListener("resize", updateWidth);
    return () => {
      ro.disconnect();
      window.removeEventListener("resize", updateWidth);
    };
  }, []);

  // Stable target width calculation with reliable minimum fallback
  const baseTargetWidth = containerWidth > 150 ? containerWidth - 32 : 600;
  const targetWidth = Math.round(baseTargetWidth * (zoom || 1.0));
  const safeTargetWidth = targetWidth && !isNaN(targetWidth) && targetWidth > 100 ? targetWidth : 600;
  const currentPage = pageNumber || 1;

  // Cleanly reset viewer state when paper or file changes
  useEffect(() => {
    retryAttemptRef.current = 0;
    setNumPages(null);
    setIsPageRendered(false);
    setRenderError(null);
    const target = getTargetPage(activeCitation);
    setPageNumber(target);
  }, [fileUrl, paperId]);

  // Zero-Failure Watchdog: If canvas does not confirm completion within 1500ms, auto-fallback to native iframe
  useEffect(() => {
    if (useIframeFallback || isPageRendered) return;
    const timer = setTimeout(() => {
      if (!isPageRendered) {
        console.warn("PDF canvas render delayed (>1500ms): Auto-engaging native iframe fallback.");
        setUseIframeFallback(true);
      }
    }, 1500);
    return () => clearTimeout(timer);
  }, [fileUrl, paperId, pageNumber, isPageRendered, useIframeFallback]);

  // Sync pageNumber when activeCitation changes
  useEffect(() => {
    if (!activeCitation) return;
    const targetPage = getTargetPage(activeCitation);
    setPageNumber((prev) => (prev === targetPage ? prev : targetPage));
  }, [activeCitation]);

  // Track page render status across page transitions
  useEffect(() => {
    setIsPageRendered(false);
    setRenderError(null);
  }, [pageNumber]);

  useEffect(() => {
    if (!scrollContainerRef.current) return;
    const container = scrollContainerRef.current;

    if (!activeCitation) {
      container.scrollTop = 0;
      return;
    }

    const target =
      activeCitation.page_num ??
      activeCitation.page_number ??
      activeCitation.page ??
      1;
    const targetPage = Number(target);

    // Wait until the target page is mounted and fully rendered before scrolling
    if (pageNumber !== targetPage) {
      return;
    }

    if (!isPageRendered) {
      return;
    }

    const scrollTimer = setTimeout(() => {
      // 1. Try scrolling directly to the rendered overlay element
      const highlightEl = container.querySelector("#citation-highlight-overlay");
      if (highlightEl) {
        highlightEl.scrollIntoView({ behavior: "smooth", block: "center" });
        return;
      }

      // 2. Fallback coordinate calculation
      const citation = activeCitation;
      const pHeight = Number(citation.page_height) || 792;
      let rawTop = Number(
        Array.isArray(citation.bbox) ? citation.bbox[1] : (citation.bbox_top ?? citation.bbox_y0 ?? 0)
      );
      let rawY1 = Number(
        Array.isArray(citation.bbox) ? citation.bbox[3] : (citation.bbox_y1 ?? 0)
      );

      if (rawTop > rawY1 && rawY1 > 0) {
        const temp = rawTop;
        rawTop = rawY1;
        rawY1 = temp;
      }

      const isPoints = (rawY1 > 1.0) || (rawTop > 1.0);
      const normTop = isPoints ? (rawTop / pHeight) * 100 : rawTop * 100;

      if (normTop > 0 && normTop <= 100) {
        const scrollableH = container.scrollHeight;
        const targetScroll = (normTop / 100) * scrollableH - container.clientHeight / 3;
        const maxScroll = Math.max(0, scrollableH - container.clientHeight);
        container.scrollTo({
          top: Math.max(0, Math.min(maxScroll, targetScroll)),
          behavior: "smooth"
        });
      } else {
        container.scrollTo({ top: 0, behavior: "smooth" });
      }
    }, 120);

    return () => clearTimeout(scrollTimer);
  }, [activeCitation, pageNumber, zoom, isPageRendered]);

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
    if (activeCitation) {
      const targetPage = getTargetPage(activeCitation);
      setPageNumber((prev) => {
        const clamped = Math.min(targetPage, numPages);
        return prev === clamped ? prev : clamped;
      });
      return;
    }
    setPageNumber((prev) => (prev >= 1 && prev <= numPages ? prev : 1));
  }

  function onPageRenderSuccess() {
    setIsPageRendered(true);
    setRenderError(null);
    retryAttemptRef.current = 0;
  }

  function onPageRenderError(error) {
    // If a render task was cancelled due to navigating to another page or switching documents, ignore safely
    if (
      error &&
      (error.name === "RenderingCancelledException" ||
        error.message?.toLowerCase().includes("cancelled") ||
        error.message?.toLowerCase().includes("canceled"))
    ) {
      return;
    }
    console.error("PDF page render error, falling back to native iframe viewer:", error);
    setUseIframeFallback(true);
  }

  // Memoized overlay component to prevent canvas re-renders on highlight changes
  const CitationOverlay = memo(({ citation, currentPage, isRendered }) => {
    if (!citation) return null;
    const target =
      citation.page_num ??
      citation.page_number ??
      citation.page ??
      1;
    const targetPage = Number(target);
    if (currentPage !== targetPage) return null;
    // Only render overlay after page is fully rendered to prevent race condition
    if (!isRendered) return null;

    const pWidth = Number(citation.page_width) || 612;
    const pHeight = Number(citation.page_height) || 792;

    let rawX0 = 0;
    let rawTop = 0;
    let rawX1 = 0;
    let rawY1 = 0;

    if (Array.isArray(citation.bbox) && citation.bbox.length === 4) {
      rawX0 = Number(citation.bbox[0] ?? 0);
      rawTop = Number(citation.bbox[1] ?? 0);
      rawX1 = Number(citation.bbox[2] ?? 0);
      rawY1 = Number(citation.bbox[3] ?? 0);
    } else {
      rawX0 = Number(citation.bbox_x0 ?? 0);
      rawTop = Number(citation.bbox_top ?? citation.bbox_y0 ?? 0);
      rawX1 = Number(citation.bbox_x1 ?? 0);
      rawY1 = Number(citation.bbox_y1 ?? 0);
    }

    // Handle inversion if coordinates were passed in reverse order
    if (rawTop > rawY1 && rawY1 > 0) {
      const temp = rawTop;
      rawTop = rawY1;
      rawY1 = temp;
    }
    if (rawX0 > rawX1 && rawX1 > 0) {
      const temp = rawX0;
      rawX0 = rawX1;
      rawX1 = temp;
    }

    const hasExplicitBbox = (rawX1 > rawX0) || (rawY1 > rawTop) || (rawX0 > 0 || rawTop > 0 || rawX1 > 0 || rawY1 > 0);

    let left, top, width, height;

    if (hasExplicitBbox && (rawX1 > rawX0 || rawY1 > rawTop)) {
      const isPoints = rawX1 > 1.0 || rawY1 > 1.0 || rawX0 > 1.0 || rawTop > 1.0;

      const normX0 = isPoints ? (rawX0 / pWidth) * 100 : rawX0 * 100;
      const normTop = isPoints ? (rawTop / pHeight) * 100 : rawTop * 100;
      const normX1 = isPoints ? (rawX1 / pWidth) * 100 : rawX1 * 100;
      const normY1 = isPoints ? (rawY1 / pHeight) * 100 : rawY1 * 100;

      left = Math.max(0, Math.min(95, normX0));
      top = Math.max(0, Math.min(95, normTop));
      width = Math.max(6, Math.min(100 - left, normX1 - normX0));
      // Clamp height smoothly, min 2.5%, max 20%
      height = Math.min(Math.max(2.5, Math.min(100 - top, normY1 - normTop)), 20);
    } else {
      // Fallback bounding box for chunks without extracted word boxes (e.g. plain text or table chunks with 0,0,0,0)
      left = 8;
      top = 10;
      width = 84;
      height = 8;
    }

    const isNearTop = top < 4;

    return (
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          zIndex: 10,
          pointerEvents: "none",
        }}
      >
        {/* DOM Bounding Box Anchor Highlight with semi-transparent amber background & solid border */}
        <div
          id="citation-highlight-overlay"
          className="absolute pointer-events-none rounded transition-all duration-300"
          style={{
            position: "absolute",
            left: `${left}%`,
            top: `${top}%`,
            width: `${width}%`,
            height: `${height}%`,
            backgroundColor: "rgba(245, 158, 11, 0.22)",
            border: "2px solid #f59e0b",
            mixBlendMode: "multiply",
            borderRadius: "4px",
            boxShadow: "0 0 10px rgba(245, 158, 11, 0.35)",
            zIndex: 10,
            pointerEvents: "none",
          }}
        >
          <span
            className="absolute left-0 px-2 py-0.5 text-[9.5px] font-mono font-bold bg-[#f59e0b] text-[#060b10] rounded shadow-md tracking-wider uppercase whitespace-nowrap pointer-events-none"
            style={{
              zIndex: 11,
              pointerEvents: "none",
              ...(isNearTop
                ? { top: "100%", marginTop: "4px" }
                : { bottom: "100%", marginBottom: "4px" }),
            }}
          >
            ✦ CITATION BOUNDING-BOX ANCHOR (PAGE {targetPage})
          </span>
        </div>
      </div>
    );
  });

  return (
    <div className="flex flex-col h-full rounded-2xl bg-[#08131b] border border-[#16323b] shadow-2xl overflow-hidden overflow-x-hidden">
      
      {/* Viewer Header & View Controls Toolbar */}
      <div className="px-4 py-2.5 bg-[#060b10] border-b border-[#16323b] flex flex-wrap items-center justify-between gap-2 z-20">
        <div className="flex items-center gap-2 max-w-[36%]">
          <FileText className="w-4 h-4 text-[#2dd4ce] shrink-0" />
          <span className="font-mono text-xs font-semibold text-white truncate" title={filename}>
            {filename || "Active Source Document"}
          </span>
        </div>

        {/* View Controls Toolbar */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {/* Mode Switcher Toggle */}
          <button
            type="button"
            onClick={() => setUseIframeFallback((prev) => !prev)}
            className={`px-2 py-1 rounded-lg text-[10.5px] font-mono font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
              useIframeFallback
                ? "bg-[#2dd4ce]/20 text-[#2dd4ce] border border-[#2dd4ce]/50 shadow-sm"
                : "bg-white/5 text-[#8fa89b] hover:text-white hover:bg-white/10 border border-white/10"
            }`}
            title={useIframeFallback ? "Switch to Canvas View" : "Switch to Native High-DPI Embed"}
          >
            <Sparkles className="w-3 h-3 text-[#2dd4ce]" />
            <span>{useIframeFallback ? "⚡ Native Embed" : "🎨 Canvas Mode"}</span>
          </button>

          {/* Page Navigation */}
          <div className="flex items-center gap-1 font-mono text-xs text-[#8fa89b] px-2 py-1 bg-white/5 rounded-lg border border-white/10">
            <button
              type="button"
              disabled={pageNumber <= 1}
              onClick={() => setPageNumber((prev) => Math.max(prev - 1, 1))}
              className="p-1 hover:text-white disabled:opacity-30 cursor-pointer transition-colors"
              title="Previous Page"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <span className="px-1 text-[11px] font-mono text-[#d8f3f0] whitespace-nowrap">
              Page {pageNumber} {numPages ? `of ${numPages}` : ""}
            </span>
            <button
              type="button"
              disabled={numPages ? pageNumber >= numPages : false}
              onClick={() => setPageNumber((prev) => (numPages ? Math.min(prev + 1, numPages) : prev + 1))}
              className="p-1 hover:text-white disabled:opacity-30 cursor-pointer transition-colors"
              title="Next Page"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Zoom Controls & Fit to Width */}
          {!useIframeFallback && (
            <div className="flex items-center gap-1 bg-white/5 px-1.5 py-0.5 rounded-lg border border-white/10">
              <button
                type="button"
                onClick={() => setZoom((z) => Math.max(0.5, Math.round((z - 0.15) * 100) / 100))}
                className="p-1 rounded text-[#8fa89b] hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
                title="Zoom Out (-)"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>

              <span className="font-mono text-[11px] text-[#2dd4ce] min-w-[38px] text-center">
                {Math.round(zoom * 100)}%
              </span>

              <button
                type="button"
                onClick={() => setZoom((z) => Math.min(2.5, Math.round((z + 0.15) * 100) / 100))}
                className="p-1 rounded text-[#8fa89b] hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
                title="Zoom In (+)"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>

              <div className="w-[1px] h-3.5 bg-white/10 mx-0.5" />

              {/* Fit to Width button */}
              <button
                type="button"
                onClick={() => setZoom(1.0)}
                className={`px-2 py-0.5 rounded text-[10.5px] font-mono font-semibold transition-all cursor-pointer flex items-center gap-1 ${
                  zoom === 1.0
                    ? "bg-[#2dd4ce]/20 text-[#2dd4ce] border border-[#2dd4ce]/40 shadow-sm"
                    : "text-[#8fa89b] hover:text-white hover:bg-white/10 border border-transparent"
                }`}
                title="Fit to Width (100%)"
              >
                <Maximize2 className="w-3 h-3" />
                <span>Fit Width</span>
              </button>
            </div>
          )}

          <a
            href={fileUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-[#8fa89b] hover:text-white transition-colors"
            title="Open original PDF in new tab"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </a>

          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-[#ff4757] hover:bg-[#ff4757]/10 transition-colors cursor-pointer"
            title="Close Source Pane"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Highlighted Claim Box */}
      {activeCitation && (
        <div className="px-4 py-2.5 bg-[#0a1f26] border-b border-[#2dd4ce]/30 flex flex-col gap-1">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono text-[#2dd4ce] uppercase tracking-wider flex items-center gap-1 font-bold">
              <MapPin className="w-3 h-3 text-[#2dd4ce]" />
              ANCHORED PASSAGE // CHUNK #{activeCitation.chunk_index ?? activeCitation.chunk_id ?? 1} (PAGE {activeCitation.page_num ?? activeCitation.page_number ?? activeCitation.page ?? 1})
            </span>
            <span className="text-[10px] font-mono text-[#d4af37] bg-[#d4af37]/15 px-2 py-0.5 rounded border border-[#d4af37]/30">
              Grounded Citation
            </span>
          </div>
          <p className="text-xs text-[#d8f3f0] italic line-clamp-2 leading-snug">
            "{activeCitation.snippet || activeCitation.full_text || activeCitation.citation || "Passage verified in literature index."}"
          </p>
        </div>
      )}

      {/* PDF Document Render Surface */}
      <div
        ref={scrollContainerRef}
        className={`flex-1 overflow-y-auto ${
          zoom <= 1.0 ? "overflow-x-hidden" : "overflow-x-auto"
        } bg-[#03070a] p-4 flex justify-center items-start no-scrollbar relative`}
      >
        {useIframeFallback ? (
          <div className="w-full h-full flex flex-col items-center justify-start min-h-[85vh]">
            <iframe
              key={`native-${currentPaperId}-p${currentPage}`}
              src={`${fileUrl}#page=${currentPage}&toolbar=0`}
              title={filename}
              className="w-full h-full rounded-xl border border-[#16323b] bg-white shadow-2xl"
              style={{ border: "none", minHeight: "85vh", width: "100%", height: "100%" }}
            />
          </div>
        ) : (
          <Document
            key={fileUrl}
            file={fileUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={(err) => {
              console.error("PDF Load Error:", err);
              setUseIframeFallback(true);
            }}
            loading={
              <div className="p-8 text-center text-xs font-mono text-[#2dd4ce] animate-pulse">
                Mounting scientific PDF layer...
              </div>
            }
            error={
              <div className="p-6 text-center space-y-3">
                <AlertCircle className="w-6 h-6 text-[#e8a33d] mx-auto" />
                <p className="text-xs text-[#adc2b6]">
                  Standard PDF canvas stream unavailable. Switching to embedded native frame viewer.
                </p>
                <button
                  type="button"
                  onClick={() => setUseIframeFallback(true)}
                  className="px-3 py-1.5 rounded-lg bg-[#2dd4ce]/20 text-[#2dd4ce] text-xs font-mono border border-[#2dd4ce]/40 cursor-pointer"
                >
                  Load Native Iframe Viewer
                </button>
              </div>
            }
          >
            {renderError ? (
              <div className="flex flex-col items-center justify-center p-8 my-12 text-center rounded-2xl bg-[#0b1820] border border-[#ff4757]/30 max-w-md mx-auto shadow-2xl">
                <div className="w-12 h-12 rounded-full bg-[#ff4757]/15 border border-[#ff4757]/30 flex items-center justify-center mb-3">
                  <AlertCircle className="w-6 h-6 text-[#ff4757]" />
                </div>
                <h3 className="text-sm font-bold text-white mb-1">Canvas Render Interrupted</h3>
                <p className="text-xs text-[#8fa89b] mb-4 leading-relaxed">
                  The canvas context encountered an interruption while rendering this document.
                </p>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      retryAttemptRef.current = 0;
                      setRenderError(null);
                      setIsPageRendered(false);
                      setRetryKey((k) => k + 1);
                    }}
                    className="px-4 py-2 rounded-lg bg-[#2dd4ce] text-[#060b10] text-xs font-mono font-bold hover:bg-[#20b8b2] transition-colors cursor-pointer flex items-center gap-2 shadow-lg"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Reload Viewer</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setUseIframeFallback(true)}
                    className="px-3 py-2 rounded-lg bg-white/10 text-white text-xs font-mono hover:bg-white/15 transition-colors cursor-pointer"
                  >
                    Load Native Frame
                  </button>
                </div>
              </div>
            ) : (
              <div
                className="relative shadow-2xl rounded-lg border border-[#16323b] [&_.react-pdf\_\_Page\_\_canvas]:z-0 [&_.react-pdf\_\_Page\_\_canvas]:relative [&_.react-pdf\_\_Page\_\_canvas]:m-0 [&_.react-pdf\_\_Page\_\_canvas]:mx-auto [&_.react-pdf\_\_Page\_\_canvas]:block [&_.react-pdf\_\_Page\_\_canvas]:[image-rendering:-webkit-optimize-contrast] [&_.react-pdf\_\_Page\_\_canvas]:[text-rendering:geometricPrecision]"
                style={{
                  imageRendering: "-webkit-optimize-contrast",
                  textRendering: "geometricPrecision",
                  width: safeTargetWidth,
                }}
                ref={pageContainerRef}
              >
                <Page
                  key={`${currentPaperId}-${currentPage}-${safeTargetWidth}${retryKey ? `-${retryKey}` : ""}`}
                  pageNumber={currentPage}
                  width={safeTargetWidth}
                  renderMode="canvas"
                  renderTextLayer={false}
                  renderAnnotationLayer={false}
                  onRenderSuccess={onPageRenderSuccess}
                  onRenderError={onPageRenderError}
                  onLoadError={(err) => {
                    console.error("Page Load Error:", err);
                    setUseIframeFallback(true);
                  }}
                >
                  <CitationOverlay
                    citation={activeCitation}
                    currentPage={currentPage}
                    isRendered={isPageRendered}
                  />
                </Page>
                {!isPageRendered && (
                  <div className="absolute top-3 right-3 px-3 py-1.5 rounded-full bg-[#060b10]/85 backdrop-blur-md border border-[#2dd4ce]/40 flex items-center gap-2 z-20 pointer-events-none shadow-xl">
                    <Loader2 className="w-3.5 h-3.5 text-[#2dd4ce] animate-spin" />
                    <span className="text-[11px] font-mono text-[#8fa89b]">Rendering page canvas...</span>
                  </div>
                )}
              </div>
            )}
          </Document>
        )}
      </div>

      {/* Footer Info */}
      <div className="px-4 py-2 bg-[#060b10] border-t border-[#16323b] flex items-center justify-between text-[11px] font-mono text-[#8fa89b]">
        <span className="truncate max-w-[280px]">FILE: {filename}</span>
        <span className="text-[#2dd4ce]">DUAL-PANE CITATION SYNC</span>
      </div>

    </div>
  );
}
