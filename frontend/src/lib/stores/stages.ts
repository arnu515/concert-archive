import { fetch } from '$lib/util/fetch';
import type { Stage } from '$lib/util/types';
import { get, writable } from 'svelte/store';
import { addToasts } from './toasts';
import token from './token';

const stages = writable<Stage[]>([]);

export async function fetchAllStages(limit = 20, offset = 0) {
	const res = await fetch(`/api/stages/all?limit=${limit}&offset=${offset}`, {
		headers: { Authorization: 'Bearer ' + get(token) }
	});
	const data = await res.json();
	if (res.ok) stages.update((old) => [...new Set([...old, ...data.stages])]);
	else addToasts([{ message: data.message, class: 'error', title: 'An error occured.' }]);
}

export default stages;
