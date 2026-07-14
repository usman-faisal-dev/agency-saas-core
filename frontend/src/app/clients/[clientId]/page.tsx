import React from "react";

interface ClientPageProps {
    params: {
        clientId: string;
    };
}

export default function ClientPage({ params }: ClientPageProps) {
    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold">Client Profile</h1>
            <p className="text-gray-500">Viewing Client ID: {params.clientId}</p>
        </div>
    );
}