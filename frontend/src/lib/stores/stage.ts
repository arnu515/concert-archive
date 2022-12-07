import type { Stage } from '$lib/util/types';
import { writable } from 'svelte/store';

export const currentStage = writable<Stage | null>(null);
