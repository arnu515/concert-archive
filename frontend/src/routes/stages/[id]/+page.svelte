<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount, onDestroy } from 'svelte';
	import { user, token } from '$lib/stores/token';
	import type { PageData } from './$types';
	import {
		currentStage,
		stageToken,
		stageRoom,
		stageReconnecting,
		leaveStage,
		connectToStage,
		stageCanSpeak,
		chatMessages,
		stageSpeakers
	} from '$lib/stores/stage';
	import { addToasts } from '$lib/stores/toasts';
	import type { Stage } from '$lib/util/types';
	import { fetch } from '$lib/util/fetch';
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
	import Participant from '$lib/components/Participant.svelte';

	export let data: PageData;
	const stage = data.stage as Stage;
	$currentStage = { ...stage };
	let hasRequestedToSpeak = false;
	let requestToSpeakTimeout: NodeJS.Timeout | null = null;
	let typedMessage = '';
	let isSendingChatMessage = false;
	let messagesBox: HTMLDivElement | undefined;
	let isTogglingSpeaker = false;

	onMount(async () => {
		if (!$user) return goto('/auth?next=' + encodeURIComponent(window.location.pathname));
		console.info('Joining stage');
		console.log($stageRoom, $stageToken, $currentStage);
		if ($stageRoom) {
			console.info('Already connected to a stage');
			return;
		}

		const res = await fetch(`/api/stage/${stage.id}/token`, {
			headers: { Authorization: 'Bearer ' + $token }
		});
		const data = await res.json();
		if (!res.ok) {
			console.error(res.status, 'Could not join stage', data);
			addToasts([
				{
					title: 'Could not join stage',
					class: 'alert-error',
					message: 'You could not join the stage. Press F12 for details.'
				}
			]);
			$currentStage = null;
			return;
		}

		$stageToken = data.token;
		await connectToStage($stageToken!, () => {
			addToasts([
				{
					title: 'Disconnected',
					class: 'alert-warning',
					message: 'You were disconnected from the stage.'
				}
			]);
		});

		return () => {
			if (requestToSpeakTimeout) clearTimeout(requestToSpeakTimeout);
		};
	});

	async function requestToSpeak() {
		if (!$stageRoom) return;
		if ($stageCanSpeak) {
			addToasts([
				{
					title: 'Failed',
					class: 'alert-warning',
					message: 'You already have permission to speak on this stage.'
				}
			]);
			return;
		}
		if (hasRequestedToSpeak) {
			addToasts([
				{
					title: 'Failed',
					class: 'alert-warning',
					message:
						'You have already requested to speak on this stage. Please wait a bit before doing it again'
				}
			]);
			return;
		}

		hasRequestedToSpeak = true;
		requestToSpeakTimeout = setTimeout(() => (hasRequestedToSpeak = false), 300000);

		const res = await fetch(`/api/stage/${stage.id}/request_to_speak`, {
			method: 'POST',
			headers: { Authorization: 'Bearer ' + $token, 'X-Livekit-Token': $stageToken! }
		});
		if (!res.ok) {
			const data = await res.json();
			console.error(res.status, 'Failed to request to speak', data);
			addToasts([
				{
					title: 'Failed',
					class: 'alert-warning',
					message: 'Failed to request to speak. Press F12 for details.'
				}
			]);
		}
	}

	async function sendMessage() {
		if (isSendingChatMessage) return;
		if (!typedMessage.trim()) return;
		isSendingChatMessage = true;
		const res = await fetch(`/api/stage/${stage.id}/chat`, {
			method: 'POST',
			headers: {
				Authorization: 'Bearer ' + $token,
				'X-Livekit-Token': $stageToken!,
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ message: typedMessage.trim() })
		});
		isSendingChatMessage = false;
		if (!res.ok) {
			const data = await res.json();
			console.error(res.status, 'Failed to send message', data);
			addToasts([
				{
					title: 'Failed',
					class: 'alert-warning',
					message: 'Failed to send message. Press F12 for details.'
				}
			]);
		}

		typedMessage = '';
	}

	async function toggleSpeaker(p: { identity: string }, toggle: boolean) {
		if (isTogglingSpeaker) return;
		isTogglingSpeaker = true;
		const res = await fetch(
			`/api/stage/${stage.id}/owner/make_${toggle ? 'speaker' : 'listener'}`,
			{
				method: 'POST',
				headers: {
					Authorization: 'Bearer ' + $token,
					'X-Livekit-Token': $stageToken!,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ user_id: p.identity })
			}
		);
		isTogglingSpeaker = false;
		if (!res.ok) {
			const data = await res.json();
			console.error(res.status, 'Failed to toggle speaker', data);
			addToasts([
				{
					title: 'Failed',
					class: 'alert-warning',
					message: 'Failed to toggle speaker. Press F12 for details.'
				}
			]);
		}
	}

	// onDestroy(() => {
	//   console.info("Leaving stage")
	//   leaveStage()
	// })

	// $: if (!$currentStage) {
	//   goto("/")
	// }
	$: console.log({ room: $stageRoom, token: $stageToken, stage: $currentStage });

	$: if ($chatMessages) {
		if (messagesBox?.lastChild) {
			(messagesBox.lastChild as HTMLDivElement).scrollIntoView({ behavior: 'smooth' });
		}
	}
</script>

{#if $stageReconnecting}
	<div class="fixed top-0 left-0 grid h-full w-full place-items-center">
		<div class="rounded-xl border-2 border-error bg-base-300 px-6 py-4 text-center">
			<h1 class="my-4 text-4xl font-bold">Reconnecting to stage</h1>
			<div class="my-4 flex items-center justify-center"><LoadingSpinner /></div>
			<div class="my-4 flex items-center justify-center">
				<button
					class="btn-error btn"
					on:click={() => {
						if (window.confirm('Are you sure?')) leaveStage();
					}}>Disconnect</button
				>
			</div>
		</div>
	</div>
{:else if $stageRoom && $user && $currentStage}
	<main>
		<div
			class="flex flex-col gap-2 overflow-hidden rounded-xl border bg-base-300 px-6 py-4"
			style="border-color: {stage.color}"
		>
			<h1
				class="mb-4 mt-4 flex min-h-[2.5rem] items-center gap-4 truncate text-3xl font-bold"
				style="color: {stage.color}"
			>
				<span class="text-white">Stage:</span>
				{stage.name}
			</h1>
			<div class="flex min-h-[4rem] items-center gap-4 overflow-x-auto pb-4">
				{#if $stageCanSpeak}
					<button class="btn-primary btn gap-4 text-white">
						{#if true}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-5 w-5"
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
							</svg> Unmute
						{:else}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-5 w-5"
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
							</svg> Mute
						{/if}
					</button>
				{:else}
					<button
						class="btn-accent btn gap-4"
						title="Request to speak"
						aria-label="Request to speak"
						disabled={hasRequestedToSpeak}
						on:click={requestToSpeak}
					>
						{#if true}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-5 w-5"
								viewBox="0 0 24 24"
								stroke-width="1.5"
								stroke="currentColor"
								fill="none"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
								<path stroke="none" d="M0 0h24v24H0z" fill="none" />
								<path d="M18 8a3 3 0 0 1 0 6" />
								<path d="M10 8v11a1 1 0 0 1 -1 1h-1a1 1 0 0 1 -1 -1v-5" />
								<path
									d="M12 8h0l4.524 -3.77a0.9 .9 0 0 1 1.476 .692v12.156a0.9 .9 0 0 1 -1.476 .692l-4.524 -3.77h-8a1 1 0 0 1 -1 -1v-4a1 1 0 0 1 1 -1h8"
								/>
							</svg>
							{hasRequestedToSpeak ? 'Requested' : 'Request to speak'}
						{:else}
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-5 w-5"
								viewBox="0 0 24 24"
								stroke-width="1.5"
								stroke="currentColor"
								fill="none"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
								<path stroke="none" d="M0 0h24v24H0z" fill="none" />
								<path d="M5 4h6a3 3 0 0 1 3 3v7" />
								<path d="M10 10l4 4l4 -4m-8 5l4 4l4 -4" />
							</svg> Become a listener
						{/if}
					</button>
				{/if}
				<button
					class="btn-outline btn-error btn ml-auto"
					on:click={() => {
						if (window.confirm('Are you sure?')) {
							leaveStage();
							goto('/');
						}
					}}>Exit Stage</button
				>
			</div>
			<h3 class="my-6 text-xl font-black uppercase">Speakers ({$stageSpeakers.length})</h3>
			<div class="flex min-h-[8rem] gap-6 overflow-x-auto pb-4">
				{#each Array.from($stageRoom?.participants.values()).filter( (i) => $stageSpeakers.includes(i.identity) ) as p}
					<Participant
						isOwner={$user.id === stage.owner_id}
						on:toggleSpeaker={() => toggleSpeaker(p, false)}
						{p}
						isSpeaker
					/>
				{/each}
				{#if $stageSpeakers.includes($stageRoom?.localParticipant?.identity)}
					<Participant p={$stageRoom.localParticipant} isSpeaker />
				{/if}
			</div>

			<!-- +1 below to account for localParticipant, which is not there in room.participants -->
			<h3 class="my-6 text-xl font-black uppercase">
				Listeners ({$stageRoom.participants.size + 1 - $stageSpeakers.length})
			</h3>
			<div class="flex flex-wrap gap-6 overflow-auto">
				{#each Array.from($stageRoom?.participants.values()).filter((i) => !$stageSpeakers.includes(i.identity)) as p}
					<Participant
						isOwner={$user.id === stage.owner_id}
						on:toggleSpeaker={() => toggleSpeaker(p, true)}
						{p}
					/>
				{/each}
				{#if !$stageSpeakers.includes($stageRoom.localParticipant?.identity)}
					<Participant p={$stageRoom.localParticipant} />
				{/if}
			</div>
		</div>
		<div
			class="flex flex-col gap-2 overflow-hidden rounded-xl border bg-base-300 px-6 py-4"
			style="border-color: {stage.color}"
		>
			<h2
				class="my-4 flex items-center justify-between text-5xl font-bold"
				style="color: {stage.color}"
			>
				Chat
			</h2>
			<div class="messages my-2 flex flex-col gap-8 pr-2" bind:this={messagesBox}>
				{#each $chatMessages as message}
					{#if message.type === 'TEXT'}
						<div class="flex items-center gap-2">
							<img
								src={message.user.avatar_url}
								alt="{message.user.username}'s avatar"
								class="h-6 w-6 rounded-full border border-white"
							/>
							<span><strong>{message.user.username}</strong>:</span>
							<span>{message.message_data}</span>
						</div>
					{:else if message.type === 'FILE'}
						<div class="flex flex-col justify-center gap-2">
							<div class="flex items-center gap-2">
								<img
									src={message.user.avatar_url}
									alt="{message.user.username}'s avatar"
									class="h-6 w-6 rounded-full border border-white"
								/>
								<span><strong>{message.user.username}</strong> uploaded a file</span>
							</div>
							{#if /.*\.(png|jpeg|gif|webp)/.test(message.message_data)}
								<a
									href={message.message_data}
									target="_blank"
									rel="noreferrer"
									class="my-1 flex w-full items-center"
								>
									<img
										src={message.message_data}
										class="w-full rounded"
										alt="Uploaded by {message.user.username}"
									/>
								</a>
							{:else if /.*\.(mp4|webm)/.test(message.message_data)}
								<a
									href={message.message_data}
									target="_blank"
									rel="noreferrer"
									class="my-1 flex w-full items-center"
								>
									<video controls src={message.message_data} class="w-full rounded" />
								</a>
							{:else if /.*\.(mp3|aac|ogg|flac)/.test(message.message_data)}
								<a
									href={message.message_data}
									target="_blank"
									rel="noreferrer"
									class="my-1 flex w-full items-center"
								>
									<audio controls src={message.message_data} class="w-full rounded" />
								</a>
							{:else}
								<div
									class="my-4 flex items-center rounded-xl border border-gray-500 bg-base-100 px-4 py-2"
								>
									<p class="font-mono text-xl">
										<span class="badge badge-accent uppercase"
											>{message.message_data.split('.').pop()}</span
										>
										{message.message_data.split('/').pop()}
									</p>
									<a
										href={message.message_data}
										target="_blank"
										rel="noreferrer"
										class="btn-ghost btn-sm btn-circle btn ml-auto"
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
												d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"
											/>
										</svg></a
									>
								</div>
							{/if}
						</div>
					{:else if message.type === 'EVENT'}
						{#if message.message_data === 'REQUEST_TO_SPEAK'}
							<div class="flex items-center justify-center gap-2">
								<img
									src={message.user.avatar_url}
									alt="{message.user.username}'s avatar"
									class="h-6 w-6 rounded-full border border-white"
								/>
								<span><strong>{message.user.username}</strong></span>
								<span class="text-gray-500">wishes to speak</span>
							</div>
						{:else if message.message_data === 'MADE_SPEAKER'}
							<div class="flex items-center justify-center gap-2">
								<img
									src={message.user.avatar_url}
									alt="{message.user.username}'s avatar"
									class="h-6 w-6 rounded-full border border-white"
								/>
								<span><strong>{message.user.username}</strong></span>
								<span class="text-gray-500">is now a speaker</span>
							</div>
						{:else if message.message_data === 'MADE_LISTENER'}
							<div class="flex items-center justify-center gap-2">
								<img
									src={message.user.avatar_url}
									alt="{message.user.username}'s avatar"
									class="h-6 w-6 rounded-full border border-white"
								/>
								<span><strong>{message.user.username}</strong></span>
								<span class="text-gray-500">is now a listener</span>
							</div>
						{/if}
					{/if}
				{/each}
				<div class="my-2" />
			</div>
			<input
				disabled={isSendingChatMessage}
				readonly={isSendingChatMessage}
				type="text"
				class="input m-1 mt-auto w-full"
				placeholder="Type message and press enter"
				aria-label="Message"
				bind:value={typedMessage}
				on:keypress={(e) => {
					if (e.key.toLowerCase() === 'enter' && !!typedMessage.trim()) {
						sendMessage();
					}
				}}
			/>
		</div>
	</main>
{:else}
	<div class="mt-20 flex items-center justify-center"><LoadingSpinner /></div>
{/if}

<style lang="postcss">
	main {
		@apply max-h-[1000px] px-2 md:px-4;
		display: grid;
		gap: 1rem;
	}

	.messages {
		@apply my-4 overflow-auto;
		scrollbar-width: thin;
		scrollbar-color: theme(colors.primary) theme(colors.base-300);
	}
	.messages::-webkit-scrollbar {
		width: 2px;
		background-color: theme(colors.base-300);
	}
	.messages::-webkit-scrollbar-thumb {
		width: 2px;
		background-color: theme(colors.primary);
	}

	@screen sm {
		main {
			margin: 1rem 2rem;
			grid-template-columns: 1fr;
			grid-template-rows: 3fr 1fr;
		}
	}
	@screen md {
		main {
			margin: 2rem 4rem;
			height: 90vh;
			grid-template-columns: 3fr 1fr;
			grid-template-rows: 1fr;
		}
	}
</style>
