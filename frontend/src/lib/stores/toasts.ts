import { writable } from 'svelte/store';

export interface Toast {
	id: string;
	title: string;
	message: string;
	class?: string;
}

const toasts = writable<Toast[]>([]);

export function addToasts(toast: Omit<Toast, 'id'>[]) {
	toasts.update((t) => [
		...t,
		...toast.map((t) => ({ ...t, id: Math.random().toString(36).substring(2, 10) }))
	]);
}

export default toasts;
