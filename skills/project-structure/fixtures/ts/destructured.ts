// Regression anchor: destructured exports must emit each BOUND name (one entry per
// element, kind `c`), never the raw `{ … }` binding-pattern text.
export function plainFn(x: number): number {
  return x + 1;
}

export class PlainClass {
  value = 1;
}

export type PlainType = { a: string };

export const plainConst = 42;

export const makeThing = () => ({ list: () => [], get: () => null, pair: [1, 2] as const });

export const {
  list: listThings,
  get: getThing,
} = makeThing();

export const [firstThing, secondThing] = makeThing().pair;

export * from './reexported.js';
