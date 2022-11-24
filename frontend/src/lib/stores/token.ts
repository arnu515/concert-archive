import type { User } from '$lib/util/types';
import { writable } from 'svelte/store';

export const token = writable<string | null>(null);
export const timeout = writable<NodeJS.Timeout | null>(null);
export const tokenLoading = writable<boolean>(true);
export const user = writable<User | null>(null);

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
		tokenLoading.set(false);
		return;
	}

	const res2 = await f('/api/auth/me', {
		headers: { Authorization: 'Bearer ' + json.access_token }
	});
	const json2: { user: User } = await res2.json();
	if (res.ok) {
		user.set(json2.user);
	} else {
		token.set(null);
		user.set(null);
	}

	tokenLoading.set(false);
}

export default token;
