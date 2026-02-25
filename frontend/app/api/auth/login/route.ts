import { NextRequest, NextResponse } from 'next/server';
import { authService } from '../../../../lib/auth';
import { cookies } from 'next/headers';

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json();

    if (!email || !password) {
      return NextResponse.json({ error: 'Email and password are required' }, { status: 400 });
    }

    console.log('Login attempt for:', email);
    console.log('authService status:', authService ? 'exists' : 'undefined');
    if (authService) {
      console.log('authService.login type:', typeof authService.login);
    }

    const authResponse = await authService.login({ email, password });

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
    console.error('Login API error:', error);
    const status = error.status || 500;
    return NextResponse.json({ error: error.message }, { status });
  }
}