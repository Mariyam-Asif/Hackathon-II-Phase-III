import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const BACKEND_URL = process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'http://localhost:8000';

async function proxyRequest(request: NextRequest, userId: string, path: string[]) {
  const token = (await cookies()).get('better-auth.session_token')?.value;

  if (!token) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // Path is already the array of segments after [userId]
  // e.g., /api/[userId]/tasks -> path = ["tasks"]
  // e.g., /api/[userId]/chat -> path = ["chat"]
  // e.g., /api/[userId]/tasks/123/complete -> path = ["tasks", "123", "complete"]
  
  const backendPath = path ? path.join('/') : '';
  const url = `${BACKEND_URL}/api/${userId}/${backendPath}`;
  
  console.log(`Proxying ${request.method} to: ${url}`);
  
  const method = request.method;
  const headers: Record<string, string> = {
    'Authorization': `Bearer ${token}`,
  };

  const contentType = request.headers.get('content-type');
  if (contentType) {
    headers['Content-Type'] = contentType;
  }

  let body = undefined;
  if (method !== 'GET' && method !== 'HEAD' && method !== 'DELETE') {
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

export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}

export async function GET(request: NextRequest, { params }: { params: { userId: string, path: string[] } }) {
  const { userId, path } = await params;
  return proxyRequest(request, userId, path || []);
}

export async function POST(request: NextRequest, { params }: { params: { userId: string, path: string[] } }) {
  const { userId, path } = await params;
  return proxyRequest(request, userId, path || []);
}

export async function PUT(request: NextRequest, { params }: { params: { userId: string, path: string[] } }) {
  const { userId, path } = await params;
  return proxyRequest(request, userId, path || []);
}

export async function PATCH(request: NextRequest, { params }: { params: { userId: string, path: string[] } }) {
  const { userId, path } = await params;
  return proxyRequest(request, userId, path || []);
}

export async function DELETE(request: NextRequest, { params }: { params: { userId: string, path: string[] } }) {
  const { userId, path } = await params;
  return proxyRequest(request, userId, path || []);
}
