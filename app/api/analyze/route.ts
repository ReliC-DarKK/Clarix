import { NextRequest, NextResponse } from "next/server"

const BACKEND_URL = "http://127.0.0.1:8000"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get("file")

    if (!(file instanceof File)) {
      return NextResponse.json(
        {
          success: false,
          error: "No image file provided",
        },
        { status: 400 }
      )
    }

    const backendFormData = new FormData()

    backendFormData.append("file", file)

    const response = await fetch(
      `${BACKEND_URL}/analyze`,
      {
        method: "POST",
        body: backendFormData,
      }
    )

    // Read backend response ONCE
    const data = await response.json()

    console.log("BACKEND RESPONSE:", data)

    console.log(
      "BACKEND METRICS:",
      data?.result?.psnr,
      data?.result?.ssim
    )

    if (!response.ok) {
      return NextResponse.json(
        data,
        {
          status: response.status,
        }
      )
    }

    if (!data.success) {
      return NextResponse.json(
        data,
        {
          status: 500,
        }
      )
    }

    const jobId = data.job_id

    return NextResponse.json({
      success: true,

      job_id: jobId,

      filename: data.filename,

      result: {
        // Pipeline output paths
        raw:
          data.result?.raw ??
          `${BACKEND_URL}/results/${jobId}/raw`,

        hr:
          data.result?.hr ??
          `${BACKEND_URL}/results/${jobId}/hr`,

        lr:
          data.result?.lr ??
          `${BACKEND_URL}/results/${jobId}/lr`,

        sr:
          data.result?.sr ??
          `${BACKEND_URL}/results/${jobId}/sr`,

        bicubic:
          data.result?.bicubic ??
          `${BACKEND_URL}/results/${jobId}/bicubic`,

        // P1 evaluation
        psnr:
          typeof data.result?.psnr === "number"
            ? data.result.psnr
            : null,

        ssim:
          typeof data.result?.ssim === "number"
            ? data.result.ssim
            : null,

        // P3 evaluation
        bicubic_psnr:
          typeof data.result?.bicubic_psnr === "number"
            ? data.result.bicubic_psnr
            : null,

        bicubic_ssim:
          typeof data.result?.bicubic_ssim === "number"
            ? data.result.bicubic_ssim
            : null,

        // P4
        p4:
          data.result?.p4 ?? null,

        p4_visual:
          data.result?.p4_visual ?? null,

        landCover:
          data.result?.landCover ?? null,
      },
    })
  } catch (error) {
    console.error(
      "Analyze API error:",
      error
    )

    return NextResponse.json(
      {
        success: false,
        error: "Failed to process image",
      },
      {
        status: 500,
      }
    )
  }
}