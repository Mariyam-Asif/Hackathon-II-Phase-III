import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json();

    // Get the backend API URL from environment variables
    const apiUrl = process.env.NEXT_PUBLIC_BETTER_AUTH_URL;
    if (!apiUrl) {
      throw new Error('Backend API URL is not configured.');
    }
    const loginUrl = `${apiUrl}/auth/login`;

    // Forward the login request to the actual backend
    const apiResponse = await fetch(loginUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    // If the backend response itself is not ok, forward the error.
    if (!apiResponse.ok) {
      const errorData = await apiResponse.json();
      return NextResponse.json(errorData, { status: apiResponse.status });
    }

    // Backend response is OK (2xx). Now, safely try to get the token.
    // The response might be JSON with a token, or it could be empty (e.g., 204).
    let token;
    try {
      const data = await apiResponse.json();
      token = data.access_token;
    } catch (e) {
      // This will happen if the response body is not valid JSON (e.g., empty).
      // We can proceed, but we need to check if a token was found.
      console.warn("Could not parse JSON from auth response. This might be normal for a 204 response.");
    }

    // On successful login, extract the token and set it in a secure, HttpOnly cookie
    if (token) {
      const cookieStore = await cookies();
      
      // Set the cookie
      cookieStore.set('better-auth.session_token', token, {
        httpOnly: true, // Makes the cookie inaccessible to client-side JS
        secure: process.env.NODE_ENV === 'production', // Use secure cookies in production
        path: '/', // Accessible across the entire site
        sameSite: 'lax', // Or 'strict' for better security
        maxAge: 60 * 60 * 24 * 7, // 7 days
      });

      return NextResponse.json({ success: true }, { status: 200 });
    } else {
      // If the backend response was successful but we couldn't get a token.
      return NextResponse.json({ error: 'Authentication successful, but no token was provided.' }, { status: 500 });
    }

  } catch (error) {
    console.error('API Route /api/auth/login Error:', error);
    return NextResponse.json({ error: 'An internal server error occurred.' }, { status: 500 });
  }
}
