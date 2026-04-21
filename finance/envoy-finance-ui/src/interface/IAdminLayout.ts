export interface IMenu {
  name: string;
  icon?: any;
  path?: string;
  matcher?: string[];
  matcherStartWith?: string;
  subMenus?: IMenu[];
}

export interface MenuCategory {
  category: string;
  menus: IMenu[];
}
