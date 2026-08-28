import { NextRequest, NextResponse } from "next/server"

const BACKEND_URL = "http://127.0.0.1:8000"

export async function POST(request: NextRequest) {
  try {
    const incomingFormData = await request.formData()

    const file = incomingFormData.get("file")

    if (!(file instanceof File)) {
      return NextResponse.json(
        {
          success: false,
          error: "No image file provided",
        },
        { status: 400 }
      )
    }

    const formData = new FormData()

    formData.append("file", file)

    const response = await fetch(
      `${BACKEND_URL}/analyze`,
      {
        method: "POST",
        body: formData,
      }
    )

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(
        {
          success: false,
          error: data.detail || "Backend request failed",
        },
        { status: response.status }
      )
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Analysis API error:", error)

    return NextResponse.json(
      {
        success: false,
        error: "Could not connect to Clarix backend",
      },
      { status: 500 }
    )
  }
}