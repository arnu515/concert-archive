import { writable } from 'svelte/store';

export const token = writable<string | null>(null);
export const timeout = writable<NodeJS.Timeout | null>(null);
export const tokenLoading = writable<boolean>(true);

export async function refreshToken(f = fetch) {
	const res = await f('/api/auth/refresh', { credentials: 'include' });
	const json: { access_token: string } = await res.json();
	const t = setTimeout(() => {
		refreshToken();
	}, 1000 * 60 * 60 * 14);
	timeout.set(t);
	if (res.ok) {
		token.set(json.access_token);
	} else {
		token.set(null);
	}

	tokenLoading.set(false);
}

export default token;
