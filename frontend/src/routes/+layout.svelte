<script>
	import Navbar from '$lib/components/Navbar.svelte';
	import { timeout, tokenLoading , refreshToken} from '$lib/stores/token';
	import { onMount } from 'svelte';
	import '../app.postcss';
	import { page } from '$app/stores';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import toasts from '$lib/stores/toasts';
  import {slide} from "svelte/transition"
  import { fetchAllStages } from '$lib/stores/stages';

	onMount(async () => {
	const code = new URL(window.location.href).searchParams.get('code');
	if (code) {
		const response = await fetch('/api/auth/refresh/token', {
			method: 'POST',
			body: JSON.stringify({ code }),
			credentials: 'include'
		});
		if (!response.ok) return;
	}

	await refreshToken(fetch);
  await fetchAllStages()

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
<div class="flex items-center justify-center mt-10">
<LoadingSpinner t="4px" />
</div>
{:else}
	<Navbar />
	<slot />
{/if}

<div class="toast">
  {#each $toasts as t}
    <div class="alert rounded flex-col items-start min-w-[150px] {t.class || "alert-info"}" transition:slide>
      <h3 class="font-medium flex items-center justify-between w-full">{t.title}
      <button on:click={() => toasts.update(() => $toasts.filter(i => i.id !== t.id))} class="btn btn-circle btn-ghost btn-xs"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
</svg>
</button>
      </h3>
      <p class="text-sm">{t.title}</p>
    </div>
  {/each}
</div>
