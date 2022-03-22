<script lang="ts">
    export let lifetime=3;
    import { _ } from 'svelte-i18n';

</script>
<div>
    {$_('index.lifetime')}
</div>
<div>
    <input bind:value="{lifetime}" name="lifetime">
</div>
