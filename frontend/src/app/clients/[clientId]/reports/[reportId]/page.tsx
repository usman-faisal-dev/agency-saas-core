import React from "react";

interface ReportPageProps {
    params: {
        clientId: string;
        reportId: string;
    };
}

export default function ReportPage({ params }: ReportPageProps) {
    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold">Client Report</h1>
            <p className="text-gray-500">Viewing Client ID: {params.clientId}</p>
            <p className="text-gray-500">Report ID: {params.reportId}</p>
        </div>
    );
}