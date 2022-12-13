<script lang="ts">
	import type { Participant } from 'livekit-client';
	import { user } from '$lib/stores/token';
	import { createEventDispatcher } from 'svelte';
  import {stageCurrentlySpeaking} from "$lib/stores/stage"

	export let p: Participant;
	export let isSpeaker = false;
	export let isOwner = false;
	const m = JSON.parse(p.metadata || '{}');
	const isMe = $user?.id === p.identity;
	const d = createEventDispatcher();

  $: isSpeaking = $stageCurrentlySpeaking.find(i => i === p.identity)

	function toggleSpeaker() {
		if (!isOwner || isMe) return;
		if (
			!window.confirm(
				'Are you sure you want to make ' +
					p.name +
					' a ' +
					(isSpeaker ? 'listener' : 'speaker') +
					'?'
			)
		)
			return;
		d('toggleSpeaker');
	}
</script>

<div
	class="flex flex-col items-center justify-center gap-3 {isOwner && !isMe
		? 'hover:brightness-90 transition-all cursor-pointer'
		: ''}"
	role={isOwner && !isMe ? 'button' : undefined}
	on:click={isOwner && !isMe ? toggleSpeaker : undefined}
	title={isOwner && !isMe ? (isSpeaker ? 'Make listener' : 'Make speaker') : undefined}
>
	<img src={m.avatar_url} alt="avatar" class="h-20 w-20 rounded-full border border-white" class:!border-success={isSpeaking} />
	<p
		class="truncate text-center font-mono font-bold gap-2"
		class:badge={isSpeaker}
		style={isSpeaker
			? `background-color: ${m.color}; border-color: currentColor; color: white`
			: `color: ${m.color}`}
	>
    {#if isSpeaker}
					<span class="text-white" title={p.isMicrophoneEnabled ? "Unmuted": "Muted"}>
						{#if p.isMicrophoneEnabled}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-4 w-4"
								viewBox="0 0 24 24"
								stroke-width="1.5"
								stroke="currentColor"
								fill="none"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
								<path stroke="none" d="M0 0h24v24H0z" fill="none" />
								<rect x="9" y="2" width="6" height="11" rx="3" />
								<path d="M5 10a7 7 0 0 0 14 0" />
								<line x1="8" y1="21" x2="16" y2="21" />
								<line x1="12" y1="17" x2="12" y2="21" />
							</svg>
						{:else}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-4 w-4"
								viewBox="0 0 24 24"
								stroke-width="1.5"
								stroke="currentColor"
								fill="none"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
								<path stroke="none" d="M0 0h24v24H0z" fill="none" />
								<line x1="3" y1="3" x2="21" y2="21" />
								<path d="M9 5a3 3 0 0 1 6 0v5a3 3 0 0 1 -.13 .874m-2 2a3 3 0 0 1 -3.87 -2.872v-1" />
								<path d="M5 10a7 7 0 0 0 10.846 5.85m2.002 -2a6.967 6.967 0 0 0 1.152 -3.85" />
								<line x1="8" y1="21" x2="16" y2="21" />
								<line x1="12" y1="17" x2="12" y2="21" />
							</svg>
						{/if}
					</span>
    {/if}
		{isMe ? 'You' : m.username}
	</p>
</div>
