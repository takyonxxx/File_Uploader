FROM node:14

RUN mkdir /code
WORKDIR /code

COPY package.json ./

RUN yarn

COPY . /code/

# RUN yarn build

RUN yarn install

CMD ["yarn", "serve"]
