export const dynamic = "force-dynamic";

type RouteContext = { params: Promise<{ path: string[] }> };

const apiBaseUrl = (process.env.AVANTI_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

async function forward(request: Request, context: RouteContext): Promise<Response> {
  const { path } = await context.params;
  const headers = new Headers();
  const authorization = request.headers.get("authorization");
  const contentType = request.headers.get("content-type");

  if (authorization) headers.set("authorization", authorization);
  if (contentType) headers.set("content-type", contentType);

  const hasBody = !["GET", "HEAD"].includes(request.method);
  const response = await fetch(`${apiBaseUrl}/${path.map(encodeURIComponent).join("/")}`, {
    method: request.method,
    headers,
    body: hasBody ? await request.arrayBuffer() : undefined,
    cache: "no-store",
  });

  const responseHeaders = new Headers();
  const responseContentType = response.headers.get("content-type");
  if (responseContentType) responseHeaders.set("content-type", responseContentType);
  return new Response(response.body, { status: response.status, headers: responseHeaders });
}

export async function GET(request: Request, context: RouteContext) {
  return forward(request, context);
}

export async function POST(request: Request, context: RouteContext) {
  return forward(request, context);
}

export async function PATCH(request: Request, context: RouteContext) {
  return forward(request, context);
}

export async function DELETE(request: Request, context: RouteContext) {
  return forward(request, context);
}
