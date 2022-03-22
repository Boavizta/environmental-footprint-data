<script lang="ts">
    export let lifetime=3;
    import { _ } from 'svelte-i18n';

</script>
{$_('index.lifetime')}
<input bind:value="{lifetime}" name="lifetime" type="text">
