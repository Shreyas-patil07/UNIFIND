// Quick test to verify Supabase configuration
console.log('=== Supabase Configuration Test ===');
console.log('VITE_SUPABASE_URL:', import.meta.env.VITE_SUPABASE_URL);
console.log('VITE_SUPABASE_ANON_KEY exists:', !!import.meta.env.VITE_SUPABASE_ANON_KEY);
console.log('VITE_SUPABASE_ANON_KEY length:', import.meta.env.VITE_SUPABASE_ANON_KEY?.length);

if (!import.meta.env.VITE_SUPABASE_URL) {
  console.error('❌ VITE_SUPABASE_URL is not set!');
} else {
  console.log('✅ VITE_SUPABASE_URL is set');
}

if (!import.meta.env.VITE_SUPABASE_ANON_KEY) {
  console.error('❌ VITE_SUPABASE_ANON_KEY is not set!');
} else {
  console.log('✅ VITE_SUPABASE_ANON_KEY is set');
}

export default {};
