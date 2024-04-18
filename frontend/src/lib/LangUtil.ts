import { Meta } from "./Meta";
import { Empty } from "./Empty";

export class TryResult<T> {
  constructor(public data?: T, public error?: Error | any) {
    if (data === undefined && error === undefined) {
      throw new Meta("CannotAllUndefined", "Cannot be all undefined");
    }
  }
}

export async function tryPromise<T>(promise: Promise<T>): Promise<TryResult<T>> {
  try {
    const data: any = (await promise) ?? Empty.value;
    return new TryResult<T>(data, undefined);
  } catch (error) {
    return new TryResult<T>(undefined, error);
  }
}

export function tryBlock<T>(block: () => T): TryResult<T> {
  try {
    const data: any = block() ?? Empty.value;
    return new TryResult<T>(data, undefined);
  } catch (error) {
    return new TryResult<T>(undefined, error);
  }
}

export async function retryPromise<T>(promise: Promise<T>, retryCount: number = 1): Promise<TryResult<T>> {
  try {
    const data: any = (await promise) ?? Empty.value;
    return new TryResult<T>(data, undefined);
  } catch (error) {
    if (retryCount <= 0) {
      return new TryResult<T>(undefined, error);
    }
    return retryPromise(promise, retryCount - 1);
  }
}
