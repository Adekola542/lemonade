# Base image
FROM php:8.2-fpm

# Set working directory
WORKDIR /var/www

# Install dependencies
RUN apt-get update && apt-get install -y \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip \
    curl \
    git && \
    docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd && \
    apt-get clean

# Install Composer
COPY --from=composer:2.6 /usr/bin/composer /usr/bin/composer

# Copy existing application code
COPY . /var/www

# Set permissions
RUN chown -R www-data:www-data /var/www && chmod -R 775 /var/www/storage /var/www/bootstrap/cache

# Add Healthcheck
HEALTHCHECK --interval=30s --timeout=10s \
    CMD curl --fail http://localhost || exit 1

# Install Laravel dependencies
RUN composer install --optimize-autoloader --no-dev

# Expose port
EXPOSE 9000

# Start PHP-FPM server
CMD ["php-fpm"]
