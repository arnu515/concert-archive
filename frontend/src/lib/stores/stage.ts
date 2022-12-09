import { PUBLIC_LIVEKIT_URL } from '$env/static/public';
import { fetch } from '$lib/util/fetch';
import type { ChatMessage, Stage, User } from '$lib/util/types';
import { ParticipantEvent, RemoteParticipant, Room, RoomEvent } from 'livekit-client';
import { get, writable } from 'svelte/store';
import { addToasts } from './toasts';
import { token as userToken } from './token';

export const currentStage = writable<Stage | null>(null);
export const stageRoom = writable<Room | null>(null);
export const stageToken = writable<string | null>(null);
export const stageReconnecting = writable<boolean>(false);
export const stageCanSpeak = writable<boolean>(false);
export const chatMessages = writable<ChatMessage[]>([]);
export const stageSpeakers = writable<User['id'][]>([]);

export async function connectToStage(token: string, onDisconnect: () => void) {
	const r = new Room({
		adaptiveStream: true,
		dynacast: true,
		publishDefaults: {
			simulcast: true,
			stopMicTrackOnMute: true
		}
	});

	const startTime = Date.now();

	r.on(RoomEvent.ParticipantConnected, (p) => {
		console.log('Participant connected', p.identity, p.name, p.metadata, p.permissions);
		if (p.permissions?.canPublish) {
			stageSpeakers.update((speakers) => [...new Set([...speakers, p.identity])]);
		}
		stageRoom.set(r);
		p.on(ParticipantEvent.TrackMuted, (pub) => {
			console.log(p.name, 'muted', pub.trackSid);
			stageRoom.set(r);
		})
			.on(ParticipantEvent.TrackUnmuted, (pub) => {
				console.log(p.name, 'unmuted', pub.trackSid);
				stageRoom.set(r);
			})
			.on(ParticipantEvent.ConnectionQualityChanged, (q) => {
				console.log(p.name, 'changed connection quality', q);
				stageRoom.set(r);
			})
			.on(ParticipantEvent.IsSpeakingChanged, (s) => {
				console.log(p.name, 'changed speaking state', s);
				stageRoom.set(r);
				if (p.permissions?.canPublish) {
					stageSpeakers.update((speakers) => [...new Set([...speakers, p.identity])]);
				} else {
					stageSpeakers.update((speakers) => speakers.filter((i) => i !== p.identity));
				}
			});
	})
		.on(RoomEvent.ParticipantDisconnected, (p) => {
			console.log('Participant connected', p.identity, p.name, p.metadata);
			stageRoom.set(r);
		})
		.on(RoomEvent.DataReceived, (rawData, p) => {
			const data = new TextDecoder().decode(rawData);
			console.log('Received data', data, p ? 'from ' + p.identity : '');
			handleData(data, p);
			stageRoom.set(r);
		})
		.on(RoomEvent.ParticipantPermissionsChanged, (old, p) => {
			console.log('permission changed', old, p.permissions);
			if (!p.permissions) return;
			const { canPublish } = p.permissions;
			if (canPublish) {
				stageCanSpeak.set(true);
				stageSpeakers.update((speakers) => [...new Set([...speakers, p.identity])]);
			} else {
				stageCanSpeak.set(false);
				stageSpeakers.update((speakers) => speakers.filter((i) => i !== p.identity));
			}
			stageRoom.set(r);
		})
		.on(RoomEvent.Disconnected, (reason) => {
			console.log('Disconnected', reason);
			onDisconnect();
			stageRoom.set(null);
			currentStage.set(null);
			stageToken.set(null);
			stageSpeakers.set([]);
		})
		.on(RoomEvent.Reconnecting, () => {
			console.log('Reconnecting to room');
			stageReconnecting.set(true);
			stageRoom.set(r);
		})
		.on(RoomEvent.Reconnected, () => {
			stageRoom.set(r);
			stageReconnecting.set(false);
			console.log('Successfully reconnected. server', r.engine.connectedServerAddress);
		})
		.on(RoomEvent.LocalTrackPublished, (s) => {
			stageRoom.set(r);
			console.log('Local track published', s);
		})
		.on(RoomEvent.LocalTrackUnpublished, (s) => {
			console.log('Local track unpublished', s);
			stageRoom.set(r);
		})
		.on(RoomEvent.RoomMetadataChanged, (metadata) => {
			console.log('New metadata for room', metadata);
			stageRoom.set(r);
		})
		.on(RoomEvent.AudioPlaybackStatusChanged, () => {
			console.log('Audio playback status changed', r.canPlaybackAudio);
			stageRoom.set(r);
		})
		.on(RoomEvent.TrackSubscribed, (_t, s, p) => {
			console.log('subscribed to track', s.trackSid, p.identity);
			stageRoom.set(r);
		})
		.on(RoomEvent.TrackUnsubscribed, (_t, s, p) => {
			console.log('unsubscribed from track', s.trackSid, p.identity);
			stageRoom.set(r);
		})
		.on(RoomEvent.SignalConnected, async () => {
			const signalConnectionTime = Date.now() - startTime;
			console.log(`signal connection established in ${signalConnectionTime}ms`);
			stageRoom.set(r);
		});

	try {
		await r.connect(PUBLIC_LIVEKIT_URL, token, { autoSubscribe: true });
		stageRoom.set(r);
		const elapsed = Date.now() - startTime;
		console.log(
			`successfully connected to ${r.name} in ${Math.round(elapsed)}ms`,
			r.engine.connectedServerAddress
		);

		const res = await fetch(`/api/stage/${r.name}/chat`, {
			headers: { Authorization: `Bearer ${get(userToken)}`, 'X-Livekit-Token': token }
		});
		const data = await res.json();
		if (!res.ok) {
			addToasts([{ message: data.message, class: 'alert-error', title: 'Failed to load chat' }]);
		} else {
			chatMessages.set(data.messages);
		}
		if (r.localParticipant.permissions?.canPublish) {
			stageCanSpeak.set(true);
			stageSpeakers.update((speakers) => [...new Set([...speakers, r.localParticipant.identity])]);
		}
		stageSpeakers.update((s) => [
			...s,
			...Array.from(r.participants.values())
				.filter((p) => p.permissions?.canPublish)
				.map((p) => p.identity)
		]);
	} catch (error) {
		const message = (error as Error).message || 'unknown error';
		console.log('could not connect:', message);
		return;
	}
}

export function leaveStage() {
	const r = get(stageRoom);

	if (!r) return;

	if (r.localParticipant.isCameraEnabled) {
		r.localParticipant.setCameraEnabled(false);
	}
	if (r.localParticipant.isMicrophoneEnabled) {
		r.localParticipant.setMicrophoneEnabled(false);
	}

	r.disconnect();
	stageRoom.set(null);
	stageToken.set(null);
	stageSpeakers.set([]);
	currentStage.set(null);
}

function handleData(data: string, _p: RemoteParticipant | undefined) {
	try {
		const parsed = JSON.parse(data);
		if (typeof parsed.type !== 'string') {
			throw new Error('missing type');
		}

		switch (parsed.type.toLowerCase()) {
			case 'chat': {
				if (!parsed.data) throw new Error('CHAT: Missing chat message');
				const message = parsed.data as ChatMessage;
				// check that `message` correctly implements the ChatMessage interface
				if (typeof message.id !== 'string') throw new Error('CHAT: Missing message.id');
				if (!['TEXT', 'FILE', 'EVENT'].includes(message.type))
					throw new Error('CHAT: Invalid message.type');
				if (typeof message.message_data !== 'string')
					throw new Error('CHAT: Missing message.message_data');
				if (typeof message.stage_id !== 'string') throw new Error('CHAT: Missing message.stage_id');
				if (typeof message.user_id !== 'string') throw new Error('CHAT: Missing message.user_id');
				if (typeof message.created_at !== 'string')
					throw new Error('CHAT: Missing message.created_at');
				if (typeof message.updated_at !== 'string')
					throw new Error('CHAT: Missing message.updated_at');
				if (typeof message.user !== 'object') throw new Error('CHAT: Missing message.user');
				if (typeof message.user.username !== 'string')
					throw new Error('CHAT: Missing message.user.username');
				if (typeof message.user.avatar_url !== 'string')
					throw new Error('CHAT: Missing message.user.avatar_url');

				chatMessages.update((messages) => [...messages, message]);

				switch (message.message_data.toLowerCase()) {
					case 'made_speaker':
					case 'made_listener': {
						const r = get(stageRoom);
						if (!r) break;
						const newSpeakers: string[] = [];
						if (r.localParticipant.permissions?.canPublish) {
							newSpeakers.push(r.localParticipant.identity);
						}
						Array.from(r.participants.values()).forEach((p) => {
							if (p.permissions?.canPublish) {
								console.log(p.permissions, p.name);
								newSpeakers.push(p.identity);
							}
						});
						stageSpeakers.set([...new Set(newSpeakers)]);
						break;
					}
				}

				break;
			}
		}
	} catch (e) {
		console.error('Error while parsing', data);
		console.error(e);
	}
}
