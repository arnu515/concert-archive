import token, { refreshToken } from '$lib/stores/token';
import { get } from 'svelte/store';

export const fetch = async (url: string, options: RequestInit = {}, f = window.fetch) => {
	const res = await f(url, options);
	if (res.status === 401) {
		console.info('Refreshing token...');
		await refreshToken(f, true);
		const headers = new Headers(options.headers) || new Headers();
		headers.set('Authorization', 'Bearer ' + get(token));
		return await f(url, { ...options, headers });
	} else {
		return res;
	}
};
