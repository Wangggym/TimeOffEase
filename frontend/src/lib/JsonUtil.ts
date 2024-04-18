import {
  classToPlain,
  instanceToPlain,
  plainToClassFromExist,
  plainToInstance,
} from "class-transformer";
import { ClassTransformOptions } from "class-transformer/types/interfaces";
import { tryBlock } from "./LangUtil";
import isBlank from "@sedan-utils/is-blank";

export class JsonUtil {
  static toArrayFromType<T, V>(
    cls: { new (...args: any[]): T },
    json: V[] | string,
    options?: ClassTransformOptions
  ): T[] | undefined {
    try {
      let source = json;
      if (typeof source === "string") {
        source = JsonUtil.parse(source);
        if (source === undefined) return undefined;
      }
      return plainToInstance(cls, source as [], options);
    } catch (ex) {
      console.log(ex);
      return undefined;
    }
  }

  static toModelFromType<T, V>(
    cls: { new (...args: any[]): T },
    json: V,
    options?: ClassTransformOptions
  ): T {
    try {
      let source = json;
      if (typeof source === "string") {
        source = JsonUtil.parse(source);
        if (source === undefined) return new cls();
      }
      return plainToInstance(cls, source, options);
    } catch (ex) {
      console.log(ex);
      return new cls();
    }
  }

  static toArrayFromInstance<T, V>(clsObject: T[], json: V[]): T[] | undefined {
    try {
      return plainToClassFromExist(clsObject, json);
    } catch (ex) {
      console.log(ex);
      return undefined;
    }
  }

  static toModelFromInstance<T, V>(clsObject: T, json: V): T | undefined {
    try {
      let source = json;
      if (typeof source === "string") {
        source = JsonUtil.parse(source);
        if (source === undefined) return undefined;
      }
      return plainToClassFromExist(clsObject, source);
    } catch (ex) {
      console.log(ex);
      return undefined;
    }
  }

  static stringify(object?: any): string | undefined {
    if (object === undefined) return undefined;
    try {
      return JSON.stringify(classToPlain(object));
    } catch (ex) {
      console.log("toJson", ex);
      return undefined;
    }
  }

  static parseFromInstance(
    object: any | undefined
  ): Record<string, any> | undefined {
    if (!object) {
      return undefined;
    }
    return instanceToPlain(object);
  }

  static parse(text: string | undefined): any | undefined {
    if (!text || isBlank(text)) return undefined;

    let str = text.trimStart();
    if (!str.startsWith("{") && !str.startsWith("[")) return undefined;

    return tryBlock(() => JSON.parse(str)).data;
  }
}
