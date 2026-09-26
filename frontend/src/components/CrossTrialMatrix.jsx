import React, { useState, useEffect } from "react";
import { Scale, FileText, MapPin, Search } from "lucide-react";
import { fetchCrossTrialMatrix } from "../services/api";

export default function CrossTrialMatrix({ papers = [], onOpenPdf }) {
  const [matrixData, setMatrixData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    setLoading(true);
    fetchCrossTrialMatrix()
      .then((data) => setMatrixData(data || []))
      .catch((err) => console.warn("Matrix fetch failed:", err))
      .finally(() => setLoading(false));
  }, [papers]);

  const filteredRows = matrixData.filter(
    (row) =>
      row.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      row.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
      row.primary_endpoint.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="rounded-2xl bg-[#08131b]/95 border border-[#16323b] p-5 shadow-xl space-y-4">
      {/* Component Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#16323b] pb-3">
        <div className="flex items-center gap-2">
          <Scale className="w-4 h-4 text-[#e8a33d]" />
          <h2 className="font-mono text-xs font-bold text-white uppercase tracking-wider">
            CROSS-TRIAL QUANTITATIVE METRIC MATRIX
          </h2>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Filter endpoints..."
              className="pl-8 pr-3 py-1 rounded-xl bg-[#060b10] border border-[#16323b] text-white text-xs placeholder:text-[#5d736a] focus:border-[#2dd4ce] focus:outline-none"
            />
            <Search className="w-3.5 h-3.5 text-[#8fa89b] absolute left-2.5 top-2" />
          </div>
          <span className="text-[10px] font-mono text-[#2dd4ce] bg-[#2dd4ce]/10 px-2.5 py-0.5 rounded-full border border-[#2dd4ce]/30">
            {filteredRows.length} TRIALS
          </span>
        </div>
      </div>

      {/* Tabular Comparison */}
      <div className="overflow-x-auto no-scrollbar">
        <table className="w-full text-left border-collapse text-xs font-sans">
          <thead>
            <tr className="border-b border-[#16323b] bg-[#060b10]/80 font-mono text-[11px] text-[#8fa89b] uppercase tracking-wider">
              <th className="py-3 px-4">Clinical Trial / Document</th>
              <th className="py-3 px-4">Sample Size (N)</th>
              <th className="py-3 px-4">Primary Endpoint</th>
              <th className="py-3 px-4">Effect Size / HR</th>
              <th className="py-3 px-4">P-Value</th>
              <th className="py-3 px-4 text-right">Bounding-Box Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#16323b]/60">
            {loading && (
              <tr>
                <td colSpan={6} className="py-8 text-center font-mono text-xs text-[#2dd4ce] animate-pulse">
                  Synthesizing trial quantitative endpoints...
                </td>
              </tr>
            )}

            {!loading && filteredRows.length === 0 && (
              <tr>
                <td colSpan={6} className="py-8 text-center font-mono text-xs text-[#8fa89b]">
                  No clinical trial metrics found matching search query.
                </td>
              </tr>
            )}

            {!loading &&
              filteredRows.map((row, idx) => (
                <tr
                  key={row.paper_id || idx}
                  className="hover:bg-[#0c222a]/60 transition-colors group"
                >
                  <td className="py-3.5 px-4">
                    <div className="flex items-start gap-2">
                      <FileText className="w-3.5 h-3.5 text-[#2dd4ce] shrink-0 mt-0.5" />
                      <div>
                        <p className="font-bold text-white line-clamp-1 group-hover:text-[#2dd4ce] transition-colors">
                          {row.title}
                        </p>
                        <p className="font-mono text-[10px] text-[#8fa89b]">{row.filename}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 font-mono font-bold text-[#adc2b6]">
                    {row.sample_size}
                  </td>
                  <td className="py-3.5 px-4 text-[#d8f3f0]">
                    {row.primary_endpoint}
                  </td>
                  <td className="py-3.5 px-4 font-mono text-[#2dd4ce] font-semibold">
                    {row.effect_size}
                  </td>
                  <td className="py-3.5 px-4 font-mono font-bold text-[#d4af37]">
                    {row.p_value}
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => onOpenPdf && onOpenPdf(row.filename, row.citation)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#2dd4ce]/10 hover:bg-[#2dd4ce]/20 border border-[#2dd4ce]/40 text-[#2dd4ce] font-mono text-[11px] font-bold transition-all cursor-pointer shadow"
                    >
                      <MapPin className="w-3 h-3 text-[#2dd4ce]" />
                      <span>View in Table</span>
                    </button>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
