<script lang="ts">
	import { page } from '$app/stores';
</script>

<svelte:head>
	<title>An error occured ({$page.status})</title>
</svelte:head>

<div class="fixed top-0 left-0 grid h-full w-full place-items-center">
	<div class="rounded-xl border-2 border-error bg-base-300 px-6 py-4 text-center">
		<h1 class="my-4 text-4xl font-bold">An error occured ({$page.status})</h1>
		<p class="my-4 font-mono text-2xl font-medium">
			{$page.error?.message || 'An unknown error occured'}
		</p>
		<p class="my-4 flex items-center justify-center gap-2">
			<button class="btn-accent btn" on:click={() => history.back()}>Go back</button>
			<a class="btn-primary btn" href="/">Go home</a>
		</p>
	</div>
</div>
