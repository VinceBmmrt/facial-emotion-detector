"use client";

import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setResult(data);
    } catch (error) {
      console.error(error);
      setResult({ result: null, error: "Erreur lors de l'analyse" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4">
      <h1 className="text-2xl font-bold mb-4">Analyse d&apos;image</h1>

      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
        className="mb-4"
      />
      <button
        onClick={handleUpload}
        disabled={!file || loading}
        className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
      >
        {loading ? "Analyse en cours..." : "Analyser"}
      </button>

      {result && (
        <div className="mt-6 p-4 border rounded w-full max-w-md">
          {result.error && <p className="text-red-500">{result.error}</p>}

          {result.result ? (
            <div className="flex flex-col gap-2 text-blue-200">
              <p>
                <strong>Émotion :</strong> {result.result.emotion}
              </p>
              <p>
                <strong>Intensité :</strong> {result.result.intensity}
              </p>
              <p>
                <strong>Âge estimé :</strong> {result.result.age_estimate}
              </p>
            </div>
          ) : (
            <p>Aucune donnée disponible</p>
          )}
        </div>
      )}
    </main>
  );
}
