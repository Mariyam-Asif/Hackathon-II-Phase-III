
import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function POST() {
  try {
    (await cookies()).set('better-auth.session_token', '', {
      httpOnly: true,
      secure: process.env.NODE_ENV !== 'development',
      maxAge: -1,
      path: '/',
    });

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Logout API error:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
