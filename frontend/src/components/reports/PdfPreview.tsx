interface PdfPreviewProps {
  pdfUrl: string | null;
}

export default function PdfPreview({ pdfUrl }: PdfPreviewProps) {
  if (!pdfUrl) {
    return (
      <div className="border rounded-lg p-6 flex items-center justify-center bg-gray-50">
        <p className="text-sm text-gray-400">No PDF available</p>
      </div>
    );
  }

  return (
    <div className="border rounded-lg overflow-hidden">
      <iframe src={pdfUrl} className="w-full h-[600px]" title="Report PDF Preview" />
    </div>
  );
}
