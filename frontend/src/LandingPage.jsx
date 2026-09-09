import React, { useState } from "react";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import TrustSection from "./components/TrustSection";
import ProductShowcase from "./components/ProductShowcase";
import FaqSection from "./components/FaqSection";
import ConversionBanner from "./components/ConversionBanner";
import Footer from "./components/Footer";
import CoaModal from "./components/CoaModal";
import AllocationModal from "./components/AllocationModal";
import { useAuth } from "./AuthContext";

export default function LandingPage({ onStart, onOpenAuth, onGoWorkspace }) {
  const { isAuthenticated } = useAuth();
  const [selectedCoaId, setSelectedCoaId] = useState(null);
  const [isAllocationOpen, setIsAllocationOpen] = useState(false);
  const [allocationProduct, setAllocationProduct] = useState(null);

  const handleOpenCoa = (paperId) => {
    setSelectedCoaId(paperId || "paper-01");
  };

  const handleCloseCoa = () => {
    setSelectedCoaId(null);
  };

  const handleOpenAllocation = (product = null) => {
    setAllocationProduct(product);
    setIsAllocationOpen(true);
  };

  const handleCloseAllocation = () => {
    setIsAllocationOpen(false);
  };

  const handleStartVerification = () => {
    if (isAuthenticated) {
      onStart();
    } else {
      onOpenAuth("login");
    }
  };

  const handleScrollToBatchSearch = () => {
    const el = document.getElementById("features") || document.getElementById("workflow");
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="min-h-screen bg-[#060b10] text-[#f4f7f5] font-sans selection:bg-[#2dd4ce]/25 selection:text-[#2dd4ce] relative">
      
      {/* Top Navbar */}
      <Navbar
        onOpenBatchSearch={handleScrollToBatchSearch}
        onOpenAllocation={handleStartVerification}
        onOpenAuth={onOpenAuth}
      />

      {/* Main Sections */}
      <main>
        {/* 1. Hero Section with 3D Perspective Glass Card */}
        <Hero
          onOpenCoa={handleOpenCoa}
          onExplore={handleStartVerification}
          onExploreBenchmark={() => handleOpenCoa("paper-01")}
        />

        {/* 2. "How It Works" / 4-Step Process Section */}
        <TrustSection
          onOpenCoa={handleOpenCoa}
          onSelectBatch={handleStartVerification}
        />

        {/* 3. "Key Features" & Literature Benchmarks */}
        <ProductShowcase
          onOpenCoa={handleOpenCoa}
          onAddToOrder={handleStartVerification}
        />

        {/* 4. FAQ Section */}
        <FaqSection
          onOpenCoa={handleOpenCoa}
        />

        {/* 5. Conversion Banner */}
        <ConversionBanner />
      </main>

      {/* Luxury Footer */}
      <Footer onOpenCoa={handleOpenCoa} />

      {/* Interactive Sample Audit Modal */}
      {selectedCoaId && (
        <CoaModal
          peptideId={selectedCoaId}
          onClose={handleCloseCoa}
        />
      )}

      {/* Allocation / Batch Inspector Modal */}
      {isAllocationOpen && (
        <AllocationModal
          initialProduct={allocationProduct}
          onClose={handleCloseAllocation}
        />
      )}

    </div>
  );
}