import React, { useState, useEffect, useRef } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import {
  X,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  ExternalLink,
  FileText,
  AlertCircle,
  Sparkles,
  MapPin
} from "lucide-react";

// Configure pdfjs worker
try {
  pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;
} catch (e) {
  // fallback handled gracefully
}

export default function PdfViewer({ fileUrl, filename, activeCitation, onClose }) {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.05);
  const [useIframeFallback, setUseIframeFallback] = useState(false);

  const scrollContainerRef = useRef(null);

  useEffect(() => {
    const targetPage = activeCitation?.page_number || activeCitation?.page;
    if (targetPage && typeof targetPage === "number") {
      setPageNumber(targetPage);
    }
  }, [activeCitation]);

  useEffect(() => {
    if (!scrollContainerRef.current) return;
    const container = scrollContainerRef.current;

    if (!activeCitation) {
      container.scrollTop = 0;
      return;
    }

    const citation = activeCitation;
    const pHeight = citation.page_height || 792;
    const rawX0 = citation.bbox_x0 ?? 0;
    const rawTop = citation.bbox_top ?? citation.bbox_y0 ?? 0;
    const rawX1 = citation.bbox_x1 ?? 0;
    const rawY1 = citation.bbox_y1 ?? 0;

    const isPoints = rawX1 > 1.0 || rawY1 > 1.0;
    const normTop = isPoints ? (rawTop / pHeight) * 100 : rawTop * 100;
    const hasValidBbox = rawX1 > rawX0 && rawY1 > rawTop && normTop >= 0 && normTop <= 100;

    if (hasValidBbox && normTop > 0) {
      const scrollableH = container.scrollHeight;
      const targetScroll = (normTop / 100) * scrollableH - container.clientHeight / 3;
      const maxScroll = Math.max(0, scrollableH - container.clientHeight);
      container.scrollTop = Math.max(0, Math.min(maxScroll, targetScroll));
    } else {
      // Gracefully default to scrolling to top of page without jumping out of bounds
      container.scrollTop = 0;
    }
  }, [activeCitation, pageNumber, scale]);

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
    const targetPage = activeCitation?.page_number || activeCitation?.page;
    if (targetPage && typeof targetPage === "number") {
      setPageNumber(targetPage);
    } else {
      setPageNumber(1);
    }
  }

  // Calculate bounding box overlay coordinates with bounds checking & safety clamping
  const renderBboxOverlay = () => {
    if (!activeCitation) return null;
    const targetPage = activeCitation.page_number || activeCitation.page || 1;
    if (pageNumber !== targetPage) return null;

    const citation = activeCitation;

    const pWidth = citation.page_width || 612;
    const pHeight = citation.page_height || 792;

    let rawX0 = citation.bbox_x0 ?? 0;
    let rawTop = citation.bbox_top ?? citation.bbox_y0 ?? 0;
    let rawX1 = citation.bbox_x1 ?? 0;
    let rawY1 = citation.bbox_y1 ?? 0;

    // Handle inversion if y0 and y1 were passed in reverse
    if (rawTop > rawY1 && rawY1 > 0) {
      const temp = rawTop;
      rawTop = rawY1;
      rawY1 = temp;
    }

    const isPoints = rawX1 > 1.0 || rawY1 > 1.0;

    const normX0 = isPoints ? (rawX0 / pWidth) * 100 : rawX0 * 100;
    const normTop = isPoints ? (rawTop / pHeight) * 100 : rawTop * 100;
    const normX1 = isPoints ? (rawX1 / pWidth) * 100 : rawX1 * 100;
    const normY1 = isPoints ? (rawY1 / pHeight) * 100 : rawY1 * 100;

    // Safety bounds checking ensuring coordinates never exceed 0% to 100% of the page
    const left = Math.max(0, Math.min(100, normX0));
    const top = Math.max(0, Math.min(100, normTop));
    const width = Math.max(5, Math.min(100 - left, normX1 - normX0));
    // Clamp height to max 12% to smoothly frame top lines of excerpt without stretching across multiple paragraphs
    const height = Math.min(Math.max(2, Math.min(100 - top, normY1 - normTop)), 12);

    const hasValidBbox = rawX1 > rawX0 && rawY1 > rawTop && width > 0 && height > 0;
    if (!hasValidBbox) return null;

    const isNearTop = top < 4;

    return (
      <div
        className="absolute pointer-events-none rounded transition-all duration-300 animate-pulse z-20"
        style={{
          position: "absolute",
          left: `${left}%`,
          top: `${top}%`,
          width: `${width}%`,
          height: `${height}%`,
          maxHeight: "14%",
          backgroundColor: "rgba(234, 179, 8, 0.25)",
          border: "2px solid #EAB308",
          borderRadius: "4px",
          boxShadow: "0 0 10px rgba(234, 179, 8, 0.4)",
          pointerEvents: "none",
        }}
      >
        <span
          className="absolute left-0 px-2 py-0.5 text-[9.5px] font-mono font-bold bg-[#e8a33d] text-[#060b10] rounded shadow-md tracking-wider uppercase whitespace-nowrap pointer-events-none z-30"
          style={{
            pointerEvents: "none",
            ...(isNearTop
              ? { top: "100%", marginTop: "4px" }
              : { bottom: "100%", marginBottom: "4px" }),
          }}
        >
          ✦ CITATION BOUNDING-BOX ANCHOR (PAGE {targetPage})
        </span>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full rounded-2xl bg-[#08131b] border border-[#16323b] shadow-2xl overflow-hidden">
      
      {/* Viewer Header */}
      <div className="px-4 py-3 bg-[#060b10] border-b border-[#16323b] flex items-center justify-between">
        <div className="flex items-center gap-2 max-w-[55%]">
          <FileText className="w-4 h-4 text-[#2dd4ce] shrink-0" />
          <span className="font-mono text-xs font-semibold text-white truncate" title={filename}>
            {filename || "Active Source Document"}
          </span>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          {!useIframeFallback && numPages && (
            <div className="flex items-center gap-1 font-mono text-xs text-[#8fa89b] px-2 py-1 bg-white/5 rounded-lg border border-white/10">
              <button
                disabled={pageNumber <= 1}
                onClick={() => setPageNumber((prev) => Math.max(prev - 1, 1))}
                className="p-1 hover:text-white disabled:opacity-30 cursor-pointer"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <span>{pageNumber} / {numPages}</span>
              <button
                disabled={pageNumber >= numPages}
                onClick={() => setPageNumber((prev) => Math.min(prev + 1, numPages))}
                className="p-1 hover:text-white disabled:opacity-30 cursor-pointer"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {!useIframeFallback && (
            <div className="flex items-center gap-1">
              <button
                onClick={() => setScale((s) => Math.max(s - 0.15, 0.6))}
                className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-[#8fa89b] hover:text-white transition-colors cursor-pointer"
                title="Zoom Out"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setScale((s) => Math.min(s + 0.15, 2.2))}
                className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-[#8fa89b] hover:text-white transition-colors cursor-pointer"
                title="Zoom In"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          <a
            href={fileUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-[#8fa89b] hover:text-white transition-colors"
            title="Open in new window"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </a>

          <button
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
              ANCHORED PASSAGE // CHUNK #{activeCitation.chunk_index ?? activeCitation.page ?? 1}
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
      <div ref={scrollContainerRef} className="flex-1 overflow-auto bg-[#03070a] p-4 flex justify-center items-start no-scrollbar relative">
        {useIframeFallback ? (
          <iframe
            src={fileUrl}
            title={filename}
            className="w-full h-full rounded-xl border border-[#16323b] bg-white"
          />
        ) : (
          <Document
            file={fileUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={() => setUseIframeFallback(true)}
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
                  onClick={() => setUseIframeFallback(true)}
                  className="px-3 py-1.5 rounded-lg bg-[#2dd4ce]/20 text-[#2dd4ce] text-xs font-mono border border-[#2dd4ce]/40 cursor-pointer"
                >
                  Load Native Iframe Viewer
                </button>
              </div>
            }
          >
            <div className="relative inline-block shadow-2xl rounded-lg border border-[#16323b]">
              <Page
                pageNumber={pageNumber}
                scale={scale}
                renderTextLayer={true}
                renderAnnotationLayer={true}
              />
              {renderBboxOverlay()}
            </div>
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
