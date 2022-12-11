<script lang="ts">
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import StageItem from '$lib/components/StageItem.svelte';
	import stages, { fetchAllStages } from '$lib/stores/stages';
	import { addToasts } from '$lib/stores/toasts';

	let page = 1;
	let isLoading = false;
	let canLoadMore = true;

	async function loadMore() {
		if (!canLoadMore || isLoading) return;
		isLoading = true;
		const stg = [...$stages];
		await fetchAllStages(20, page * 20);
		if ($stages.length - stg.length < 20) {
			canLoadMore = false;
			addToasts([
				{
					title: 'No more stages to load',
					message: 'There are no more stages to load',
					class: 'alert-warning'
				}
			]);
		}
		page++;
		isLoading = false;
	}

	async function refresh() {
		if (isLoading) return;
		isLoading = true;
		page = 0;
		$stages = [];
		await fetchAllStages();
		canLoadMore = true;
		page++;
		isLoading = false;
	}
</script>

<main>
	<div class="flex flex-col gap-2">
		<h1 class="mb-12 flex items-center justify-between text-7xl font-bold">
			Discover Stages
			<button
				on:click={refresh}
				class="btn-accent btn-square btn text-white"
				title="Refresh"
				aria-label="Refresh"
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
						d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
					/>
				</svg></button
			>
		</h1>
		<form class="input-group mb-4 flex items-center">
			<input
				type="search"
				class="input-bordered input w-full"
				placeholder="Search for a stage"
				aria-label="Search"
			/>
			<button class="btn-primary btn text-white" title="Search" aria-label="Search">
				<svg
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
						d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
					/>
				</svg>
			</button>
		</form>
		{#if Array.isArray($stages) && $stages.length > 0}
			{#each $stages as stage}
				<StageItem {stage} />
			{/each}
			<div class="mt-8 flex items-center justify-center">
				{#if canLoadMore}
					<button
						class="btn-secondary btn text-white"
						on:click={loadMore}
						disabled={isLoading}
						class:loading={isLoading}>Load more</button
					>
				{/if}
			</div>
		{:else if !isLoading}
			<p class="text-2xl">No stages found.</p>
		{/if}
		{#if isLoading}
			<div class="mt-8 flex items-center justify-center">
				<LoadingSpinner />
			</div>
		{/if}
	</div>
	<div />
</main>

<style lang="postcss">
	main {
		display: grid;
		gap: 1rem;
	}

	@screen sm {
		main {
			margin: 1rem 2rem;
			grid-template-columns: 1fr;
		}
	}
	@screen md {
		main {
			margin: 2rem 4rem;
			grid-template-columns: 3fr 1fr;
		}
	}
</style>
