<script lang="ts">
    export let region = "EU";
    import { _ } from 'svelte-i18n';

</script>
{$_('index.select_location')}
<input name="region" type="text" bind:value={region}>
