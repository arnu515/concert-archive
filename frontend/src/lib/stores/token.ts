import type { User } from '$lib/util/types';
import { writable } from 'svelte/store';

export const token = writable<string | null>(null);
export const timeout = writable<NodeJS.Timeout | null>(null);
export const tokenLoading = writable<boolean>(true);
export const user = writable<User | null>(null);

export async function refreshToken(f = fetch, force = false) {
	const tokenFromSS = sessionStorage.getItem('token');
	const userFromSS = sessionStorage.getItem('user');
	const expFromSS = sessionStorage.getItem('exp');

	if (
		typeof tokenFromSS === 'string' &&
		typeof userFromSS === 'string' &&
		typeof expFromSS === 'string'
	) {
		try {
			if (force) throw new Error();
			const u = JSON.parse(userFromSS);
			if (Date.now() > Number(expFromSS)) throw new Error();
			if (
				typeof u.id !== 'string' ||
				typeof u.email !== 'string' ||
				typeof u.username !== 'string' ||
				typeof u.avatar_url !== 'string' ||
				typeof u.created_at !== 'string'
			)
				throw new Error();
			if (tokenFromSS.split('.')?.length !== 3) throw new Error();

			token.set(tokenFromSS);
			user.set(u);

			const t = setTimeout(() => {
				refreshToken();
			}, 1000 * 60 * 60 * 14);
			timeout.set(t);

			tokenLoading.set(false);
			return;
		} catch (e) {
			console.error(e);
			sessionStorage.removeItem('token');
			sessionStorage.removeItem('user');
			sessionStorage.removeItem('exp');
			token.set(null);
			user.set(null);
		}
	}

	const res = await f('/api/auth/refresh', { credentials: 'include' });
	const json: { access_token: string } = await res.json();
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

	const t = setTimeout(() => {
		refreshToken();
	}, 1000 * 60 * 60 * 14);
	timeout.set(t);

	sessionStorage.setItem('token', json.access_token);
	sessionStorage.setItem('exp', (Date.now() + 1000 * 60 * 60 * 14).toString());
	sessionStorage.setItem('user', JSON.stringify(json2.user));

	tokenLoading.set(false);
}

export default token;
