<script>
	import Navbar from '$lib/components/Navbar.svelte';
	import { timeout, tokenLoading } from '$lib/stores/token';
	import { onMount } from 'svelte';
	import '../app.postcss';
	import { page } from '$app/stores';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';

	onMount(() => {
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
