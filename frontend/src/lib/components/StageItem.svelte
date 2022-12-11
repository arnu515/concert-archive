<script lang="ts">
	import type { Stage } from '$lib/util/types';
	import { user } from '$lib/stores/token';

	export let stage: Stage;
</script>

<a
	href="/stages/{stage.id}"
	class="flex cursor-pointer flex-col justify-center gap-2 rounded-xl border-2 bg-base-300 px-6 py-3"
	style="border-color: {stage.color}"
>
	<h3 class="flex items-center justify-between text-2xl font-medium" style="color: {stage.color}">
		{stage.name}
		<span class="text-sm text-gray-500">{stage.id}</span>
	</h3>
	<div class="flex items-center justify-between text-lg">
		<p class="flex items-center gap-2">
			<img
				src={stage.owner.avatar_url}
				class="h-8 w-8 rounded-full border border-white"
				alt="{stage.owner.username}'s avatar"
			/>
			{stage.owner.username}
		</p>
		<div class="flex items-center gap-2">
			{#if stage.owner_id === $user?.id}
				<span class="badge-warning badge">Your stage</span>
			{/if}
			{#if stage.private}
				<span class="badge-accent badge uppercase">Private</span>
			{/if}
		</div>
	</div>
</a>
