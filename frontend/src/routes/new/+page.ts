import { tokenLoading, user } from '$lib/stores/token';
import { redirect } from '@sveltejs/kit';
import { get } from 'svelte/store';

export function load() {
	if (get(tokenLoading) === false) {
		if (!get(user)) {
			throw redirect(302, '/auth');
		}
	}
}
