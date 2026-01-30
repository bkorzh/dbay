import type { IModule, JsonModule } from "../../state/systemState.svelte";
import { CoreModule } from "../../state/systemState.svelte";

// module placeholder
export class empty implements IModule {
  public core: CoreModule;
  constructor(data: JsonModule) {
    this.core = new CoreModule(data.core);

  }

  public update(data: JsonModule): void {
    this.core.update(data.core);
  }
}
