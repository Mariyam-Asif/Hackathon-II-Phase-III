import { NextRequest, NextResponse } from 'next/server';
import { authService } from '../../../../lib/auth';
import { cookies } from 'next/headers';

export async function POST(request: NextRequest) {
  try {
    const { email, password, username } = await request.json();

    if (!email || !password || !username) {
      return NextResponse.json({ error: 'Email, password, and username are required' }, { status: 400 });
    }

    const authResponse = await authService.register({ email, password, username });

    if (authResponse.access_token) {
      (await cookies()).set('better-auth.session_token', authResponse.access_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV !== 'development',
        maxAge: 60 * 60 * 24 * 7, // 1 week
        path: '/',
      });
    }

    return NextResponse.json(authResponse);
  } catch (error: any) {
    console.error('Registration API error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}