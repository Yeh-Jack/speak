<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';

export interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
  text_zh?: string;
}

interface Props {
  src: string;
  poster?: string;
  transcript?: TranscriptSegment[];
  autoPlay?: boolean;
  showZh?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  autoPlay: false,
  showZh: false,
});

const emit = defineEmits<{
  timeUpdate: [time: number];
  ended: [];
  paused: [];
  ready: [];
  playPause: [isPlaying: boolean];
}>();

const videoRef = ref<HTMLVideoElement | null>(null);
const containerRef = ref<HTMLDivElement | null>(null);
const isPlaying = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const volume = ref(1);
const isMuted = ref(false);
const isFullscreen = ref(false);
const showControls = ref(true);
const playbackRate = ref(1);
const showSubtitles = ref(true);
const buffered = ref(0);

let controlsTimeout: ReturnType<typeof setTimeout> | null = null;

const currentSubtitle = computed(() => {
  if (!props.transcript || !showSubtitles.value) return null;
  return props.transcript.find(
    (seg) => currentTime.value >= seg.start && currentTime.value <= seg.end
  );
});

const progress = computed(() => {
  if (duration.value === 0) return 0;
  return (currentTime.value / duration.value) * 100;
});

const formattedCurrentTime = computed(() => formatTime(currentTime.value));
const formattedDuration = computed(() => formatTime(duration.value));

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function togglePlay() {
  if (!videoRef.value) return;
  if (isPlaying.value) {
    videoRef.value.pause();
  } else {
    videoRef.value.play();
  }
}

function handleTimeUpdate() {
  if (!videoRef.value) return;
  currentTime.value = videoRef.value.currentTime;
  emit('timeUpdate', currentTime.value);

  if (videoRef.value.buffered.length > 0) {
    buffered.value = (videoRef.value.buffered.end(0) / duration.value) * 100;
  }
}

function handleLoadedMetadata() {
  if (!videoRef.value) return;
  duration.value = videoRef.value.duration;
  emit('ready');
}

function handlePlay() {
  isPlaying.value = true;
}

function handlePause() {
  isPlaying.value = false;
  emit('paused');
}

function togglePlayPause() {
  if (!videoRef.value) return;
  if (isPlaying.value) {
    videoRef.value.pause();
  } else {
    videoRef.value.play();
  }
  emit('playPause', !isPlaying.value);
}

function handleEnded() {
  isPlaying.value = false;
  emit('ended');
}

function seek(event: MouseEvent) {
  if (!videoRef.value || !containerRef.value) return;
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect();
  const percent = (event.clientX - rect.left) / rect.width;
  videoRef.value.currentTime = percent * duration.value;
}

function seekForward(seconds = 10) {
  if (!videoRef.value) return;
  videoRef.value.currentTime = Math.min(videoRef.value.currentTime + seconds, duration.value);
}

function seekBackward(seconds = 10) {
  if (!videoRef.value) return;
  videoRef.value.currentTime = Math.max(videoRef.value.currentTime - seconds, 0);
}

function setVolume(newVolume: number) {
  if (!videoRef.value) return;
  volume.value = newVolume;
  videoRef.value.volume = newVolume;
  isMuted.value = newVolume === 0;
}

function toggleMute() {
  if (!videoRef.value) return;
  isMuted.value = !isMuted.value;
  videoRef.value.muted = isMuted.value;
}

function toggleFullscreen() {
  if (!containerRef.value) return;
  if (!document.fullscreenElement) {
    containerRef.value.requestFullscreen();
    isFullscreen.value = true;
  } else {
    document.exitFullscreen();
    isFullscreen.value = false;
  }
}

function setPlaybackRate(rate: number) {
  if (!videoRef.value) return;
  playbackRate.value = rate;
  videoRef.value.playbackRate = rate;
}

function toggleSubtitles() {
  showSubtitles.value = !showSubtitles.value;
}

function handleMouseMove() {
  showControls.value = true;
  if (controlsTimeout) clearTimeout(controlsTimeout);
  controlsTimeout = setTimeout(() => {
    if (isPlaying.value) showControls.value = false;
  }, 3000);
}

function handleKeydown(event: KeyboardEvent) {
  switch (event.code) {
    case 'Space':
      event.preventDefault();
      togglePlay();
      break;
    case 'ArrowRight':
      seekForward(5);
      break;
    case 'ArrowLeft':
      seekBackward(5);
      break;
    case 'KeyM':
      toggleMute();
      break;
    case 'KeyF':
      toggleFullscreen();
      break;
    case 'KeyC':
      toggleSubtitles();
      break;
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown);
  document.addEventListener('fullscreenchange', () => {
    isFullscreen.value = !!document.fullscreenElement;
  });
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
  if (controlsTimeout) clearTimeout(controlsTimeout);
});

defineExpose({
  play: () => videoRef.value?.play(),
  pause: () => videoRef.value?.pause(),
  seek: (time: number) => {
    if (videoRef.value) videoRef.value.currentTime = time;
  },
  getCurrentTime: () => currentTime.value,
});
</script>

<template>
  <div
    ref="containerRef"
    class="relative group bg-black rounded-lg overflow-hidden cursor-pointer"
    :class="{ 'cursor-hidden': !showControls && isPlaying }"
    @mousemove="handleMouseMove"
    @mouseleave="showControls = false"
    @click="togglePlayPause"
  >
    <video
      ref="videoRef"
      :src="src"
      :poster="poster"
      class="w-full h-full object-contain"
      @timeupdate="handleTimeUpdate"
      @loadedmetadata="handleLoadedMetadata"
      @play="handlePlay"
      @pause="handlePause"
      @ended="handleEnded"
      preload="metadata"
    />

    <div
      v-if="showSubtitles && currentSubtitle"
      class="absolute bottom-20 left-0 right-0 flex flex-col items-center justify-center pointer-events-none px-4 gap-1"
    >
      <div
        class="bg-black/80 backdrop-blur-sm text-white text-xl md:text-2xl font-medium px-6 py-3 rounded-lg max-w-4xl text-center animate-fade-in border border-white/10"
      >
        {{ currentSubtitle.text }}
      </div>
      <div
        v-if="props.showZh && currentSubtitle.text_zh"
        class="bg-black/60 backdrop-blur-sm text-learning-accent-secondary text-sm md:text-base font-medium px-4 py-1 rounded-lg max-w-4xl text-center animate-fade-in"
      >
        {{ currentSubtitle.text_zh }}
      </div>
    </div>

    <div
      class="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity"
      :class="{ 'opacity-100': !isPlaying }"
    >
      <button
        @click="togglePlay"
        class="w-20 h-20 rounded-full bg-learning-accent-primary/90 hover:bg-learning-accent-primary flex items-center justify-center transition-all transform hover:scale-105 glow-accent"
      >
        <svg v-if="!isPlaying" class="w-10 h-10 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
          <path d="M8 5v14l11-7z" />
        </svg>
        <svg v-else class="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
          <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
        </svg>
      </button>
    </div>

    <div
      class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-4 pt-16 transition-opacity duration-300"
      :class="{ 'opacity-0': !showControls && isPlaying, 'opacity-100': showControls || !isPlaying }"
    >
      <div class="flex items-center gap-2 mb-2">
        <span class="text-sm text-gray-300 font-mono">{{ formattedCurrentTime }}</span>
        <div
          class="flex-1 h-1 bg-gray-600 rounded-full cursor-pointer group/progress relative"
          @click="seek"
        >
          <div
            class="absolute inset-y-0 left-0 bg-gray-500 rounded-full"
            :style="{ width: `${buffered}%` }"
          />
          <div
            class="absolute inset-y-0 left-0 bg-learning-accent-primary rounded-full transition-all"
            :style="{ width: `${progress}%` }"
          />
          <div
            class="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-learning-accent-primary rounded-full opacity-0 group-hover/progress:opacity-100 transition-opacity"
            :style="{ left: `calc(${progress}% - 6px)` }"
          />
        </div>
        <span class="text-sm text-gray-300 font-mono">{{ formattedDuration }}</span>
      </div>

      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <button
            @click="seekBackward(10)"
            class="p-2 hover:bg-white/10 rounded-lg transition-colors"
            title="Rewind 10s"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12.5 3C17.15 3 21.08 6.03 22.47 10.22L20.1 11c-1.06-3.18-4.05-5.5-7.6-5.5-1.95 0-3.73.72-5.12 1.88L10 10H3V3l2.6 2.6C7.45 4 9.85 3 12.5 3zM10 12l-6 6h6v-6z"/>
            </svg>
          </button>

          <button
            @click="togglePlay"
            class="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <svg v-if="!isPlaying" class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
            <svg v-else class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
            </svg>
          </button>

          <button
            @click="seekForward(10)"
            class="p-2 hover:bg-white/10 rounded-lg transition-colors"
            title="Forward 10s"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M10 3c-4.65 0-9.08 2.03-11.47 6.22L.1 8C1.16 4.82 4.05 2.5 7.6 2.5c1.95 0 3.73.72 5.12 1.88L16 7h7V0l-2.6 2.6C17.55 4 15.15 3 12.5 3h-2.5zM14 12l6 6h-6v-6z"/>
            </svg>
          </button>

          <div class="flex items-center gap-1 ml-2 group/volume">
            <button
              @click="toggleMute"
              class="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <svg v-if="!isMuted && volume > 0.5" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
              </svg>
              <svg v-else-if="!isMuted && volume > 0" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM5 9v6h4l5 5V4L9 9H5z"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
              </svg>
            </button>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              :value="isMuted ? 0 : volume"
              @input="setVolume(parseFloat(($event.target as HTMLInputElement).value))"
              class="w-0 group-hover/volume:w-20 transition-all duration-200 opacity-0 group-hover/volume:opacity-100"
            />
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button
            @click="toggleSubtitles"
            class="p-2 rounded-lg transition-colors"
            :class="showSubtitles ? 'bg-learning-accent-secondary/20 text-learning-accent-secondary' : 'hover:bg-white/10 text-gray-400'"
            title="Toggle subtitles (C)"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zM4 12h4v2H4v-2zm10 6H4v-2h10v2zm6 0h-4v-2h4v2zm0-4H10v-2h10v2z"/>
            </svg>
          </button>

          <div class="flex items-center gap-1 text-sm">
            <button
              v-for="rate in [0.5, 1, 1.5, 2]"
              :key="rate"
              @click="setPlaybackRate(rate)"
              class="px-2 py-1 rounded transition-colors"
              :class="playbackRate === rate ? 'bg-learning-accent-primary text-white' : 'text-gray-400 hover:bg-white/10'"
            >
              {{ rate }}x
            </button>
          </div>

          <button
            @click="toggleFullscreen"
            class="p-2 hover:bg-white/10 rounded-lg transition-colors"
            title="Fullscreen (F)"
          >
            <svg v-if="!isFullscreen" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
            </svg>
            <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cursor-hidden {
  cursor: none;
}
</style>