<script>
	import Navbar from '$lib/components/Navbar.svelte';
	import { timeout, tokenLoading , refreshToken} from '$lib/stores/token';
	import { onMount } from 'svelte';
	import '../app.postcss';
	import { page } from '$app/stores';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';

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
