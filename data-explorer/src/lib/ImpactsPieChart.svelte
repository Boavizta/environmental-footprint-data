<script lang="ts">
    export let scope2;
    export let scope3;
    export let numberRows=0;
    import { _ } from 'svelte-i18n';

</script>

<div id="stats">
    <div class="camembert-left">
    </div>
</div>
<p>{$_('index.global-mean',{ values: {n:numberRows}})}</p>
<p>scope2 = {scope2/numberRows}</p>
<p>scope3 = {scope3/numberRows}</p>
