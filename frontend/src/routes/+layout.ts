import { browser } from '$app/environment';
import { refreshToken } from '$lib/stores/token';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ url }) => {
	if (!browser) return;
	const code = url.searchParams.get('code');
	if (code) {
		const response = await fetch('/api/auth/refresh/token', {
			method: 'POST',
			body: JSON.stringify({ code }),
			credentials: 'include'
		});
		if (!response.ok) return;
	}

	await refreshToken(fetch);
};
