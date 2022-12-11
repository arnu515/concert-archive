<script>
	import Navbar from '$lib/components/Navbar.svelte';
	import { timeout, tokenLoading } from '$lib/stores/token';
	import { onMount } from 'svelte';
	import '../app.postcss';
	import { page } from '$app/stores';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import toasts from '$lib/stores/toasts';
	import { slide } from 'svelte/transition';
	import { fetchAllStages } from '$lib/stores/stages';

	onMount(async () => {
		await fetchAllStages();

		if (window.location.search.includes('code')) {
			const qs = $page.url.searchParams;
			qs.delete('code');
			window.history.replaceState(
				{},
				document.title,
				qs.toString() ? $page.url.pathname + '?' + qs.toString() : $page.url.pathname
			);
		}

		() => {
			if ($timeout) clearTimeout($timeout);
		};
	});
</script>

{#if $tokenLoading}
	<div class="mt-10 flex items-center justify-center">
		<LoadingSpinner t="4px" />
	</div>
{:else}
	<Navbar />
	<slot />
{/if}

<div class="toast">
	{#each $toasts as t}
		<div
			class="alert min-w-[150px] flex-col items-start rounded {t.class || 'alert-info'}"
			transition:slide
		>
			<h3 class="flex w-full items-center justify-between font-medium">
				{t.title}
				<button
					on:click={() => toasts.update(() => $toasts.filter((i) => i.id !== t.id))}
					class="btn-ghost btn-xs btn-circle btn"
					><svg
						xmlns="http://www.w3.org/2000/svg"
						fill="none"
						viewBox="0 0 24 24"
						stroke-width="1.5"
						stroke="currentColor"
						class="h-5 w-5"
					>
						<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</h3>
			<p class="text-sm">{t.message}</p>
		</div>
	{/each}
</div>
