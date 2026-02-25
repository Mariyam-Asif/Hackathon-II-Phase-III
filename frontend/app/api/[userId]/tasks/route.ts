import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const BACKEND_URL = process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:8000';

async function proxyRequest(request: NextRequest, userId: string, endpoint: string) {
  const token = (await cookies()).get('better-auth.session_token')?.value;

  if (!token) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const url = `${BACKEND_URL}/api/${userId}/${endpoint}`;
  const method = request.method;
  
  const headers: Record<string, string> = {
    'Authorization': `Bearer ${token}`,
  };

  const contentType = request.headers.get('content-type');
  if (contentType) {
    headers['Content-Type'] = contentType;
  }

  let body = undefined;
  if (method !== 'GET' && method !== 'HEAD') {
    body = await request.text();
  }

  try {
    const response = await fetch(url, {
      method,
      headers,
      body,
    });

    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    const data = await response.json().catch(() => ({}));
    return NextResponse.json(data, { status: response.status });
  } catch (error: any) {
    console.error(`Proxy error for ${method} ${url}:`, error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function GET(request: NextRequest, { params }: { params: { userId: string } }) {
  const { userId } = await params;
  return proxyRequest(request, userId, 'tasks');
}

export async function POST(request: NextRequest, { params }: { params: { userId: string } }) {
  const { userId } = await params;
  return proxyRequest(request, userId, 'tasks');
}

export async function PUT(request: NextRequest, { params }: { params: { userId: string } }) {
  const { userId } = await params;
  // This needs to handle the task_id in the URL
  const taskId = request.nextUrl.pathname.split('/').pop();
  return proxyRequest(request, userId, `tasks/${taskId}`);
}

export async function PATCH(request: NextRequest, { params }: { params: { userId: string } }) {
  const { userId } = await params;
  const taskId = request.nextUrl.pathname.split('/').filter(Boolean).slice(-2, -1)[0];
  const lastPart = request.nextUrl.pathname.split('/').pop();
  return proxyRequest(request, userId, `tasks/${taskId}/${lastPart}`);
}

export async function DELETE(request: NextRequest, { params }: { params: { userId: string } }) {
  const { userId } = await params;
  const taskId = request.nextUrl.pathname.split('/').pop();
  return proxyRequest(request, userId, `tasks/${taskId}`);
}
