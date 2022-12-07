import token from '$lib/stores/token';
import { fetch } from '$lib/util/fetch';
import { error } from '@sveltejs/kit';
import { get } from 'svelte/store';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch: f }) => {
	const id = params.id;
	const res = await fetch(
		`/api/stages/${id}`,
		{ headers: { Authorization: 'Bearer ' + get(token) } },
		f
	);
	const data = await res.json();
	if (!res.ok) {
		throw error(res.status, data.message);
	} else {
		return { stage: data.stage };
	}
};
