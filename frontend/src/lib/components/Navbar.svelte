<script>
	import { user } from '$lib/stores/token';
	import { page } from '$app/stores';
</script>

<nav
	class="flex items-center justify-between border-b border-base-200 bg-base-100 px-4 py-2 text-white"
>
	<div class="flex items-center gap-4">
		{#if $page.url.pathname !== '/'}
			<button class="btn-ghost btn-sm btn-circle btn" on:click={() => history.back()}
				><svg
					xmlns="http://www.w3.org/2000/svg"
					fill="none"
					viewBox="0 0 24 24"
					stroke-width="1.5"
					stroke="currentColor"
					class="h-6 w-6"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"
					/>
				</svg></button
			>
		{:else}
			<span class="block w-8" />
		{/if}
		<a href="/" class="text-lg font-bold">Concert</a>
	</div>

	<div class="flex items-center gap-4">
		{#if !$user}
			<a href="/auth" class="btn-primary btn-sm btn rounded px-4 text-white">Sign In</a>
		{:else}
			<a href="/new" class="btn-primary btn-sm btn rounded px-4 text-white">Create stage</a>
		{/if}
		<span class="block w-8" />
	</div>
</nav>
