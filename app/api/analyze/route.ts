import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get("file");

    if (!(file instanceof File)) {
      return NextResponse.json(
        { success: false, error: "No image file provided" },
        { status: 400 }
      );
    }

    const backendFormData = new FormData();
    backendFormData.append("file", file);

    const response = await fetch(`${BACKEND_URL}/analyze`, {
      method: "POST",
      body: backendFormData,
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, {
        status: response.status,
      });
    }

    // Convert Windows file path returned by backend
    // into a browser-accessible URL.
    const jobId = data.job_id;

    return NextResponse.json({
      success: true,
      job_id: jobId,
      filename: data.filename,

      result: {
        raw: `${BACKEND_URL}/results/${jobId}/raw`,
        hr: `${BACKEND_URL}/results/${jobId}/hr`,
        lr: `${BACKEND_URL}/results/${jobId}/lr`,
        sr: `${BACKEND_URL}/results/${jobId}/sr`,
      },
    });
  } catch (error) {
    console.error("Analyze API error:", error);

    return NextResponse.json(
      {
        success: false,
        error: "Failed to process image",
      },
      { status: 500 }
    );
  }
}